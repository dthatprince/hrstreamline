from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import LLMChain
from few_shots import few_shots
import os
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_sql_query(sql_query):
    """Clean SQL query from markdown formatting and extra whitespace"""
    # Remove markdown code blocks
    sql_query = re.sub(r'```sql\w*\n?', '', sql_query)
    sql_query = re.sub(r'```\n?', '', sql_query)
    
    # Remove extra whitespace and newlines
    sql_query = sql_query.strip()
    
    # Remove any "SQLQuery:" prefix if present
    sql_query = re.sub(r'^SQLQuery:\s*', '', sql_query, flags=re.IGNORECASE)
    
    # Remove any trailing semicolon and add it back (normalize)
    sql_query = sql_query.rstrip(';') + ';'
    
    return sql_query

def safe_vectorize_examples(examples):
    """Safely convert examples to strings for vectorization"""
    vectorized = []
    for example in examples:
        # Convert all values to strings and handle None values
        text_parts = []
        for key, value in example.items():
            if value is not None:
                # Convert to string and clean up
                str_value = str(value).strip()
                if str_value:  # Only add non-empty strings
                    text_parts.append(f"{key}: {str_value}")
        
        # Join with spaces
        vectorized.append(" ".join(text_parts))
    
    return vectorized

def validate_sql_syntax(sql_query):
    """Basic SQL syntax validation"""
    # Check for common SQL injection patterns
    dangerous_patterns = [
        r';.*drop\s+table',
        r';.*delete\s+from',
        r';.*truncate',
        r';.*alter\s+table',
        r'--.*drop',
        r'/\*.*drop.*\*/'
    ]
    
    sql_lower = sql_query.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, sql_lower):
            raise ValueError(f"Potentially dangerous SQL detected: {pattern}")
    
    return True

def find_relevant_examples(question, vectorstore, k=2):
    """Find relevant examples using semantic similarity"""
    try:
        docs = vectorstore.similarity_search(question, k=k)
        relevant_examples = []
        for doc in docs:
            if hasattr(doc, 'metadata') and doc.metadata:
                relevant_examples.append(doc.metadata)
        return relevant_examples
    except Exception as e:
        logger.warning(f"Could not find relevant examples: {e}")
        return few_shots[:k]  # Fallback to first k examples

class CustomSQLChain:
    """Custom SQL chain that handles the complete flow"""
    
    def __init__(self, llm, database, vectorstore, top_k=5):
        self.llm = llm
        self.database = database
        self.vectorstore = vectorstore
        self.top_k = top_k
        
        # Create the prompt template - Updated for PostgreSQL
        self.prompt_template = PromptTemplate(
            input_variables=["table_info", "examples", "question"],
            template="""You are an expert SQL assistant for a PostgreSQL HR database.

Database Schema:
{table_info}

Here are some example questions and their SQL queries:
{examples}

Rules:
1. Generate ONLY raw SQL queries - no markdown, explanations, or code blocks
2. Use PostgreSQL syntax (not SQLite or MySQL)
3. Limit results with "LIMIT 5" when appropriate
4. Query only necessary columns
5. Use proper JOINs when accessing multiple tables
6. Handle date comparisons with PostgreSQL date functions (DATE(), CURRENT_DATE, etc.)
7. Be case-sensitive with column names as shown in schema
8. Use PostgreSQL-specific functions when needed (EXTRACT, DATE_TRUNC, etc.)
9. Use proper PostgreSQL data types and casting (::DATE, ::INTEGER, etc.)

Question: {question}
SQLQuery:"""
        )
        
        # Create the LLM chain
        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def invoke(self, inputs):
        """Main method to process queries"""
        question = inputs.get("query", "")
        logger.info(f"Processing question: {question}")
        
        try:
            # Step 1: Find relevant examples
            relevant_examples = find_relevant_examples(question, self.vectorstore, k=2)
            
            # Format examples for the prompt
            examples_text = ""
            for i, example in enumerate(relevant_examples, 1):
                examples_text += f"\nExample {i}:\n"
                examples_text += f"Question: {example.get('Question', '')}\n"
                examples_text += f"SQLQuery: {example.get('SQLQuery', '')}\n"
            
            # Step 2: Generate SQL
            llm_inputs = {
                "table_info": self.database.table_info,
                "examples": examples_text,
                "question": question
            }
            
            sql_query = self.llm_chain.predict(**llm_inputs)
            logger.info(f"Generated SQL: {sql_query}")
            
            # Clean and validate the SQL
            cleaned_sql = clean_sql_query(sql_query)
            validate_sql_syntax(cleaned_sql)
            logger.info(f"Cleaned SQL: {cleaned_sql}")
            
        except Exception as e:
            logger.error(f"Error in SQL generation: {e}")
            return f"Error generating SQL query: {str(e)}"
        
        # Step 3: Execute SQL
        try:
            sql_result = self.database.run(cleaned_sql)
            logger.info(f"SQL result: {sql_result}")
            
            # Handle empty results
            if not sql_result or sql_result.strip() == "":
                sql_result = "No results found"
                
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            return f"Error executing SQL query: {str(e)}. Please check your question and try again."
        
        # Step 4: Generate natural language answer
        answer_prompt = f"""Based on the SQL query results, provide a clear, helpful answer to the user's question.

Question: {question}
SQL Query: {cleaned_sql}
SQL Result: {sql_result}

Instructions:
- Provide a conversational, natural language response
- If no results were found, explain this clearly
- Include relevant details from the results
- Be concise but informative
- Don't mention the SQL query in your response

Answer:"""
        
        try:
            final_answer = self.llm.invoke(answer_prompt).content
            logger.info(f"Generated answer: {final_answer}")
            return final_answer.strip()
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Found results but couldn't generate a proper response: {sql_result}"
    
    def run(self, question):
        """Compatibility method for older LangChain versions"""
        return self.invoke({"query": question})

def get_few_shot_postgresql_chain():
    """Create and configure the few-shot PostgreSQL chain"""
    
    # Get database connection string from environment or use default
    database_url = os.environ.get("DEV_DATABASE_URI", "postgresql://postgres:tunga123@localhost:5432/hr_streamline_db")
    
    try:
        # Try with minimal connection first
        db = SQLDatabase.from_uri(
            database_url, 
            sample_rows_in_table_info=1,  # Minimal sample rows
            include_comments=False,       # Exclude comments to save memory
            lazy_load=True               # Enable lazy loading if available
        )
        logger.info(f"Connected to PostgreSQL database: {database_url}")
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL database with optimized settings: {e}")
        # Fallback to basic connection
        try:
            db = SQLDatabase.from_uri(database_url)
            logger.info(f"Connected with basic settings: {database_url}")
        except Exception as fallback_error:
            logger.error(f"All connection attempts failed: {fallback_error}")
            raise

    # Initialize LLM
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=0.1,
    )

    # Set up embeddings and vectorstore with error handling
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            model_kwargs={'device': 'cpu'}  # Force CPU to avoid GPU memory issues
        )
        
        # Limit the number of examples to vectorize to save memory
        limited_few_shots = few_shots[:10] if len(few_shots) > 10 else few_shots
        to_vectorize = safe_vectorize_examples(limited_few_shots)
        
        # Create vectorstore with limited examples
        vectorstore = Chroma.from_texts(
            to_vectorize, 
            embeddings, 
            metadatas=limited_few_shots,
            persist_directory=None  # Don't persist to save memory
        )
        logger.info("Vectorstore created successfully")
    except Exception as e:
        logger.error(f"Failed to create vectorstore: {e}")
        # Fallback: create a simple vectorstore with minimal examples
        try:
            embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
            fallback_examples = few_shots[:3]  # Use only first 3 examples
            to_vectorize = safe_vectorize_examples(fallback_examples)
            vectorstore = Chroma.from_texts(to_vectorize, embeddings, metadatas=fallback_examples)
            logger.info("Fallback vectorstore created")
        except Exception as fallback_error:
            logger.error(f"Fallback vectorstore also failed: {fallback_error}")
            raise

    # Create and return the custom chain
    chain = CustomSQLChain(llm, db, vectorstore)
    return chain

# Convenience function for testing
def test_chain():
    """Test the chain with a sample question"""
    try:
        chain = get_few_shot_postgresql_chain()
        test_question = "How many male employees do we have?"
        result = chain.invoke({"query": test_question})
        print(f"Question: {test_question}")
        print(f"Answer: {result}")
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    test_chain()