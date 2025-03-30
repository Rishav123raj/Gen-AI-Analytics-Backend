import re
import time
import sqlite3
from typing import Dict, List, Any, Tuple
from random import randint, choice

class QueryProcessor:
    def __init__(self, db_connection):
        self.conn = db_connection
        self._initialize_mock_database()
        
        # Define patterns for query translation
        self.patterns = [
            (r'show me (?:the )?(top|bottom) (\d+) (.+?) by (.+)', self._translate_ranking_query),
            (r'what (?:were|was) (?:the )?(.+) (?:last|this|past) (.+)', self._translate_temporal_query),
            (r'list (.+) with (.+) (?:below|under|above|over|equals to?) (.+)', self._translate_filter_query),
            (r'how many (.+) (?:were|was) there (?:last|this|past) (.+)', self._translate_count_query),
            (r'compare (.+) and (.+) by (.+)', self._translate_comparison_query),
            (r'what is the average (.+) for (.+)', self._translate_aggregation_query),
        ]
        
        # Mock table schemas
        self.schemas = {
            "customers": ["id", "name", "email", "revenue", "region", "join_date"],
            "products": ["id", "name", "category", "price", "inventory", "supplier"],
            "sales": ["id", "product_id", "customer_id", "amount", "date", "region"],
            "employees": ["id", "name", "department", "salary", "hire_date"]
        }
        
        # Mock data generators
        self.data_generators = {
            "name": lambda: choice(["John", "Jane", "Bob", "Alice", "Charlie", "Eve"]),
            "email": lambda: f"{choice(['john', 'jane', 'bob'])}@example.com",
            "revenue": lambda: randint(1000, 100000),
            "region": lambda: choice(["North", "South", "East", "West"]),
            "date": lambda: f"2023-{randint(1, 12):02d}-{randint(1, 28):02d}",
            "price": lambda: randint(10, 1000),
            "inventory": lambda: randint(0, 500),
            "amount": lambda: randint(1, 100) * 10,
            "salary": lambda: randint(30000, 120000),
            "category": lambda: choice(["Electronics", "Clothing", "Food", "Furniture"])
        }
    
    def _initialize_mock_database(self):
        """Initialize mock database tables with sample data."""
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            revenue REAL,
            region TEXT,
            join_date TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL,
            inventory INTEGER,
            supplier TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            customer_id INTEGER,
            amount REAL,
            date TEXT,
            region TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary REAL,
            hire_date TEXT
        )
        """)
        
        # Generate mock data if tables are empty
        for table in ["customers", "products", "sales", "employees"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            if cursor.fetchone()[0] == 0:
                self._generate_mock_data(table, 50)
        
        self.conn.commit()
    
    def _generate_mock_data(self, table_name: str, count: int):
        """Generate mock data for a table."""
        cursor = self.conn.cursor()
        columns = self.schemas[table_name]
        
        for _ in range(count):
            values = []
            for col in columns:
                if col.endswith("_id"):
                    values.append(randint(1, 50))
                elif col in self.data_generators:
                    values.append(self.data_generators[col]())
                elif col == "id":
                    continue  # auto-incremented
                else:
                    values.append("")
            
            placeholders = ", ".join(["?"] * len(values))
            cols = ", ".join([col for col in columns if col != "id"])
            cursor.execute(f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})", values)
    
    def process_query(self, natural_query: str) -> Dict[str, Any]:
        """Process a natural language query and return results."""
        start_time = time.time()
        
        # Translate to pseudo-SQL
        translated_query = self._translate_query(natural_query)
        
        # Execute mock query
        result = self._execute_mock_query(translated_query)
        
        return {
            "original_query": natural_query,
            "translated_query": translated_query,
            "result": result,
            "execution_time": time.time() - start_time
        }
    
    def explain_query(self, natural_query: str) -> Dict[str, Any]:
        """Explain how a query would be processed."""
        translated_query = self._translate_query(natural_query)
        explanation = self._generate_explanation(natural_query, translated_query)
        
        return {
            "original_query": natural_query,
            "explanation": explanation["summary"],
            "steps": explanation["steps"]
        }
    
    def validate_query(self, natural_query: str) -> Dict[str, Any]:
        """Validate if a query can be processed."""
        is_valid = True
        reasons = []
        suggestions = []
        
        # Check if query matches any known patterns
        matched = False
        for pattern, _ in self.patterns:
            if re.search(pattern, natural_query, re.IGNORECASE):
                matched = True
                break
        
        if not matched:
            is_valid = False
            reasons.append("Query doesn't match any known patterns")
            suggestions.append("Try using more structured queries like 'Show top X by Y' or 'List A with B under C'")
        
        # Check for known entities
        entities_found = False
        for entity in self.schemas.keys():
            if entity in natural_query.lower():
                entities_found = True
                break
        
        if not entities_found:
            is_valid = False
            reasons.append("No known data entities (customers, products, sales, etc.) detected in query")
            suggestions.append("Try mentioning specific data entities like 'customers', 'products', or 'sales'")
        
        # Check for measurable attributes
        measurable_attrs = ["revenue", "price", "inventory", "amount", "salary"]
        attr_found = any(attr in natural_query.lower() for attr in measurable_attrs)
        
        if not attr_found:
            is_valid = False
            reasons.append("No measurable attributes detected in query")
            suggestions.append("Try including measurable attributes like 'revenue', 'price', or 'inventory'")
        
        return {
            "original_query": natural_query,
            "is_valid": is_valid,
            "reasons": reasons,
            "suggestions": suggestions if not is_valid else None
        }
    
    def _translate_query(self, natural_query: str) -> str:
        """Translate natural language to pseudo-SQL."""
        natural_query = natural_query.lower()
        
        for pattern, translator in self.patterns:
            match = re.search(pattern, natural_query, re.IGNORECASE)
            if match:
                return translator(match)
        
        # Default fallback
        return f"SELECT * FROM data WHERE query='{natural_query}' LIMIT 10"
    
    def _translate_ranking_query(self, match) -> str:
        """Translate ranking queries like 'top 5 customers by revenue'."""
        direction = match.group(1)
        limit = match.group(2)
        entity = match.group(3)
        metric = match.group(4)
        
        order = "DESC" if direction == "top" else "ASC"
        
        # Map natural language to table names
        table = self._map_entity_to_table(entity)
        metric = self._map_attribute(metric)
        
        return f"SELECT * FROM {table} ORDER BY {metric} {order} LIMIT {limit}"
    
    def _translate_temporal_query(self, match) -> str:
        """Translate temporal queries like 'sales last quarter'."""
        metric = match.group(1)
        timeframe = match.group(2)
        
        # Map natural language to SQL time conditions
        time_condition = self._map_timeframe(timeframe)
        table = self._map_metric_to_table(metric)
        metric = self._map_attribute(metric)
        
        if metric == "*":
            return f"SELECT SUM(amount) FROM {table} WHERE {time_condition}"
        return f"SELECT {metric} FROM {table} WHERE {time_condition}"
    
    def _translate_filter_query(self, match) -> str:
        """Translate filter queries like 'products with inventory under 100'."""
        entity = match.group(1)
        attribute = match.group(2)
        comparison = match.group(3)
        
        table = self._map_entity_to_table(entity)
        attribute = self._map_attribute(attribute)
        operator = self._map_comparison(comparison)
        
        return f"SELECT * FROM {table} WHERE {attribute} {operator} {self._parse_value(comparison)}"
    
    def _map_entity_to_table(self, entity: str) -> str:
        """Map natural language entity to database table."""
        entity = entity.lower().rstrip('s')  # handle plurals
        if "customer" in entity:
            return "customers"
        elif "product" in entity:
            return "products"
        elif "sale" in entity:
            return "sales"
        elif "employee" in entity:
            return "employees"
        return "customers"  # default
    
    def _map_attribute(self, attribute: str) -> str:
        """Map natural language attribute to database column."""
        attribute = attribute.lower()
        if "reven" in attribute:
            return "revenue"
        elif "price" in attribute:
            return "price"
        elif "invent" in attribute:
            return "inventory"
        elif "amount" in attribute or "sale" in attribute:
            return "amount"
        elif "salar" in attribute:
            return "salary"
        return "*"
    
    def _map_timeframe(self, timeframe: str) -> str:
        """Map natural language timeframe to SQL condition."""
        timeframe = timeframe.lower()
        if "day" in timeframe:
            return "date = date('now', '-1 day')"
        elif "week" in timeframe:
            return "date >= date('now', '-7 day')"
        elif "month" in timeframe:
            return "date >= date('now', '-1 month')"
        elif "quarter" in timeframe:
            return "date >= date('now', '-3 month')"
        elif "year" in timeframe:
            return "date >= date('now', '-1 year')"
        return "1=1"  # default
    
    def _map_comparison(self, comparison: str) -> str:
        """Map natural language comparison to SQL operator."""
        comparison = comparison.lower()
        if "below" in comparison or "under" in comparison:
            return "<"
        elif "above" in comparison or "over" in comparison:
            return ">"
        elif "equal" in comparison:
            return "="
        return "="  # default
    
    def _parse_value(self, value_str: str) -> str:
        """Parse numeric values from comparison strings."""
        # Extract numbers
        numbers = re.findall(r'\d+', value_str)
        return numbers[0] if numbers else "0"
    
    def _execute_mock_query(self, pseudo_sql: str) -> List[Dict[str, Any]]:
        """Execute a mock query and return results."""
        # In a real implementation, this would execute actual SQL
        # For simulation, we'll return mock data based on the query type
        
        # Parse the pseudo-SQL to determine what to return
        if "SELECT" in pseudo_sql:
            if "SUM" in pseudo_sql or "AVG" in pseudo_sql or "COUNT" in pseudo_sql:
                # Aggregate query
                metric = re.search(r'(SUM|AVG|COUNT)\((\w+)\)', pseudo_sql)
                if metric:
                    metric_name = metric.group(2)
                    return [{f"{metric.group(1).lower()}({metric_name})": randint(1000, 100000)}]
            
            elif "ORDER BY" in pseudo_sql:
                # Ranking query
                limit = 10
                limit_match = re.search(r'LIMIT (\d+)', pseudo_sql)
                if limit_match:
                    limit = int(limit_match.group(1))
                
                table = re.search(r'FROM (\w+)', pseudo_sql).group(1)
                return self._generate_mock_records(table, limit)
            
            elif "WHERE" in pseudo_sql:
                # Filter query
                table = re.search(r'FROM (\w+)', pseudo_sql).group(1)
                return self._generate_mock_records(table, randint(1, 10))
            
            # Default select
            table = re.search(r'FROM (\w+)', pseudo_sql).group(1)
            return self._generate_mock_records(table, 5)
        
        # Default fallback
        return [{"result": "Mock data for query", "query": pseudo_sql}]
    
    def _generate_mock_records(self, table: str, count: int) -> List[Dict[str, Any]]:
        """Generate mock records for a table."""
        columns = self.schemas[table]
        records = []
        
        for _ in range(count):
            record = {}
            for col in columns:
                if col.endswith("_id"):
                    record[col] = randint(1, 50)
                elif col in self.data_generators:
                    record[col] = self.data_generators[col]()
                elif col == "id":
                    record[col] = randint(1, 1000)
                else:
                    record[col] = ""
            records.append(record)
        
        return records
    
    def _generate_explanation(self, natural_query: str, translated_query: str) -> Dict[str, Any]:
        """Generate an explanation of how the query was processed."""
        steps = [
            "Received natural language query",
            "Identified query type based on patterns",
            "Extracted key entities and attributes",
            "Mapped natural language terms to database schema",
            "Constructed structured query"
        ]
        
        summary = (
            f"The query '{natural_query}' was interpreted as a request for structured data. "
            f"The system identified relevant data entities and translated it to: {translated_query}"
        )
        
        return {
            "summary": summary,
            "steps": steps
        }