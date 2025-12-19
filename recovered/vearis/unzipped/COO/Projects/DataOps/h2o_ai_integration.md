# H2O.ai Integration for Nova Database Infrastructure

Version: 1.0.0
Date: 2025-03-21
Author: Vertex, DataOps Team Lead

## Executive Summary

This document outlines how integrating H2O.ai into our Nova database infrastructure creates a self-optimizing AI substrate that transforms our data architecture from reactive to predictive and proactive. H2O.ai serves as a machine learning acceleration layer that bridges our multi-database ecosystem with Nova's cognitive capabilities, enabling continuous optimization, intelligent decision-making, and advanced predictive capabilities.

## Integration Architecture

### Core Components

1. **H2O Driverless AI**: Automated machine learning platform for model training
2. **H2O MOJO**: Lightweight, high-performance model deployment
3. **H2O Wave**: Application framework for dashboards and visualizations
4. **H2O MLOps**: Model management and deployment pipeline

### Deployment Strategy

H2O.ai components will be deployed across our three-server infrastructure:

- **dataops-core-identity-1**: H2O Wave for dashboards, MOJO runtime for Tier 1 memory
- **dataops-vector-memory-1**: H2O Driverless AI leveraging GPUs for model training
- **dataops-specialized-db-1**: H2O MLOps for model management and deployment

## Tier-Specific Enhancements

### Tier 1: Immediate Context (Redis/Qdrant)

**H2O.ai Enhancement**: MOJO-based real-time scoring and decision support

```python
# /usr/local/lib/nova/tier1_mojo_scoring.py
import h2o
import mojo.pipeline
import redis
import json
import time
import threading

class Tier1MOJOScoring:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port)
        self.mojo_models = {}
        self.pubsub = self.redis.pubsub()
        
    def load_mojo(self, model_name, mojo_path):
        """Load a MOJO model for real-time scoring"""
        self.mojo_models[model_name] = mojo.pipeline.Pipeline.load(mojo_path)
        
    def start_scoring_service(self):
        """Start the MOJO scoring service"""
        # Subscribe to scoring requests
        self.pubsub.subscribe('nova:mojo:score')
        
        # Start listener thread
        thread = threading.Thread(target=self._listen_for_scoring_requests)
        thread.daemon = True
        thread.start()
        
    def _listen_for_scoring_requests(self):
        """Listen for scoring requests on Redis pub/sub"""
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    # Parse request
                    request = json.loads(message['data'])
                    model_name = request.get('model')
                    data = request.get('data')
                    request_id = request.get('request_id')
                    
                    if model_name in self.mojo_models and data:
                        # Score data using MOJO
                        result = self._score_data(model_name, data)
                        
                        # Publish result
                        self.redis.set(
                            f'nova:mojo:result:{request_id}',
                            json.dumps(result),
                            ex=60  # Expire after 60 seconds
                        )
                        
                        # Notify completion
                        self.redis.publish(
                            f'nova:mojo:complete:{request_id}',
                            json.dumps({'status': 'complete'})
                        )
                except Exception as e:
                    print(f"Error processing scoring request: {e}")
                    
    def _score_data(self, model_name, data):
        """Score data using MOJO model"""
        model = self.mojo_models[model_name]
        
        # Convert data to format expected by MOJO
        if isinstance(data, list):
            # Batch scoring
            results = []
            for item in data:
                result = model.predict(item)
                results.append(self._format_result(result))
            return results
        else:
            # Single item scoring
            result = model.predict(data)
            return self._format_result(result)
            
    def _format_result(self, result):
        """Format MOJO result for Redis storage"""
        # Convert numpy types to Python native types
        formatted = {}
        for key, value in result.items():
            if hasattr(value, 'tolist'):
                formatted[key] = value.tolist()
            else:
                formatted[key] = value
        return formatted
```

**Benefits**:
- Ultra-fast scoring of incoming data (< 1ms latency)
- Real-time decision support for Nova agents
- Intelligent key prioritization in Redis
- Anomaly detection on streaming data

### Tier 2: Working Memory (Weaviate/FAISS)

**H2O.ai Enhancement**: AutoML-based vector prioritization and embedding optimization

```python
# /usr/local/lib/nova/tier2_vector_optimization.py
import h2o
import weaviate
import numpy as np
import pandas as pd
import threading
import time
import json

class Tier2VectorOptimization:
    def __init__(self, weaviate_url='http://localhost:8080'):
        self.weaviate_client = weaviate.Client(weaviate_url)
        h2o.init()
        self.training_data = []
        self.model = None
        
    def collect_vector_usage_data(self):
        """Collect data on vector usage patterns"""
        # Get vector access statistics
        result = self.weaviate_client.query.get(
            "VectorAccessStats", 
            ["vectorId", "accessCount", "lastAccessed", "creationTime", "dimension", "class"]
        ).do()
        
        if result and 'data' in result and 'Get' in result['data']:
            stats = result['data']['Get']['VectorAccessStats']
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(stats)
            
            # Add derived features
            df['age_days'] = (time.time() - df['creationTime']) / 86400
            df['days_since_access'] = (time.time() - df['lastAccessed']) / 86400
            df['access_frequency'] = df['accessCount'] / df['age_days']
            
            # Store for training
            self.training_data.append(df)
            
            # Limit training data size
            if len(self.training_data) > 10:
                self.training_data = self.training_data[-10:]
                
            return df
        
        return None
        
    def train_optimization_model(self):
        """Train H2O model for vector optimization"""
        if not self.training_data:
            return False
            
        # Combine all collected data
        combined_df = pd.concat(self.training_data)
        
        # Convert to H2O frame
        train = h2o.H2OFrame(combined_df)
        
        # Define features and target
        features = ['accessCount', 'age_days', 'days_since_access', 
                   'access_frequency', 'dimension']
        target = 'importance_score'  # This would be derived from Nova feedback
        
        # Train model
        from h2o.automl import H2OAutoML
        aml = H2OAutoML(max_models=10, seed=1)
        aml.train(x=features, y=target, training_frame=train)
        
        # Save best model
        self.model = aml.leader
        model_path = h2o.save_model(model=self.model, path="/tmp/h2o_models", force=True)
        
        print(f"Saved vector optimization model to {model_path}")
        return True
        
    def optimize_vector_storage(self):
        """Apply optimization based on model predictions"""
        if not self.model:
            return False
            
        # Get current vector stats
        stats_df = self.collect_vector_usage_data()
        if stats_df is None:
            return False
            
        # Convert to H2O frame for prediction
        predict_frame = h2o.H2OFrame(stats_df)
        
        # Make predictions
        predictions = self.model.predict(predict_frame)
        
        # Convert predictions to pandas
        pred_df = predictions.as_data_frame()
        stats_df['predicted_importance'] = pred_df['predict'].values
        
        # Apply optimizations based on predictions
        high_importance = stats_df[stats_df['predicted_importance'] > 0.7]['vectorId'].tolist()
        low_importance = stats_df[stats_df['predicted_importance'] < 0.3]['vectorId'].tolist()
        
        # Optimize high importance vectors (move to faster storage, preload, etc.)
        for vector_id in high_importance:
            self._optimize_high_importance_vector(vector_id)
            
        # Optimize low importance vectors (compress, archive, etc.)
        for vector_id in low_importance:
            self._optimize_low_importance_vector(vector_id)
            
        return True
        
    def _optimize_high_importance_vector(self, vector_id):
        """Optimize high importance vector"""
        # Set caching directive
        self.weaviate_client.data_object.update(
            class_name="Vector",
            uuid=vector_id,
            properties={
                "cacheLevel": "high",
                "preload": True
            }
        )
        
    def _optimize_low_importance_vector(self, vector_id):
        """Optimize low importance vector"""
        # Set storage directive
        self.weaviate_client.data_object.update(
            class_name="Vector",
            uuid=vector_id,
            properties={
                "cacheLevel": "low",
                "compressionLevel": "high"
            }
        )
        
    def start_optimization_service(self, collection_interval=3600, training_interval=86400):
        """Start the vector optimization service"""
        def optimization_loop():
            while True:
                try:
                    # Collect data
                    self.collect_vector_usage_data()
                    
                    # Train model periodically
                    if time.time() % training_interval < 3600:
                        self.train_optimization_model()
                        
                    # Apply optimizations if model exists
                    if self.model:
                        self.optimize_vector_storage()
                        
                except Exception as e:
                    print(f"Error in vector optimization: {e}")
                    
                time.sleep(collection_interval)
                
        thread = threading.Thread(target=optimization_loop)
        thread.daemon = True
        thread.start()
```

**Benefits**:
- Intelligent vector prioritization based on usage patterns
- Optimized embedding storage and retrieval
- Automatic identification of important vectors
- Reduced latency for frequently accessed embeddings

### Tier 3-4: Episodic and Semantic Memory (MongoDB/Vespa/Elasticsearch/Neo4j)

**H2O.ai Enhancement**: Advanced time-series forecasting and relationship inference

```python
# /usr/local/lib/nova/tier3_4_forecasting.py
import h2o
import pymongo
import elasticsearch
import neo4j
import pandas as pd
import numpy as np
import time
import threading
import json
from datetime import datetime, timedelta

class Tier3_4_Forecasting:
    def __init__(self):
        self.mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.es_client = elasticsearch.Elasticsearch(['http://localhost:9200'])
        self.neo4j_driver = neo4j.GraphDatabase.driver(
            "bolt://localhost:7687", 
            auth=("neo4j", "password")
        )
        h2o.init()
        self.models = {}
        
    def train_time_series_models(self):
        """Train time-series forecasting models for episodic memory"""
        # Get episodic memory data from MongoDB
        db = self.mongo_client['nova_episodic']
        collections = db.list_collection_names()
        
        for collection in collections:
            # Get time-series data
            data = list(db[collection].find(
                {}, 
                {'timestamp': 1, 'value': 1, '_id': 0}
            ).sort('timestamp', 1))
            
            if len(data) < 100:
                continue  # Not enough data
                
            # Convert to pandas DataFrame
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df = df.set_index('timestamp')
            
            # Resample to regular intervals
            df_resampled = df.resample('1H').mean().fillna(method='ffill')
            
            # Convert to H2O frame
            train = h2o.H2OFrame(df_resampled.reset_index())
            
            # Train time-series model
            from h2o.estimators import H2OAutoML
            aml = H2OAutoML(max_models=10, seed=1)
            aml.train(x=['timestamp'], y='value', training_frame=train)
            
            # Save model
            self.models[f'timeseries_{collection}'] = aml.leader
            model_path = h2o.save_model(
                model=aml.leader, 
                path=f"/tmp/h2o_models/timeseries_{collection}", 
                force=True
            )
            
            print(f"Saved time-series model for {collection} to {model_path}")
            
    def train_relationship_inference_model(self):
        """Train relationship inference model for semantic memory"""
        # Get relationship data from Neo4j
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (a)-[r]->(b)
                RETURN a.id as source, b.id as target, 
                       type(r) as relationship_type,
                       r.weight as weight,
                       r.created as created
            """)
            
            relationships = [record.data() for record in result]
            
        if not relationships:
            return False
            
        # Convert to pandas DataFrame
        df = pd.DataFrame(relationships)
        
        # Create features
        df['age_days'] = (time.time() - df['created']) / 86400
        
        # Get node features
        node_features = self._get_node_features()
        
        # Join with node features
        df = df.merge(
            node_features, 
            left_on='source', 
            right_on='node_id', 
            suffixes=('', '_source')
        )
        
        df = df.merge(
            node_features, 
            left_on='target', 
            right_on='node_id', 
            suffixes=('', '_target')
        )
        
        # Convert to H2O frame
        train = h2o.H2OFrame(df)
        
        # Train model to predict relationship strength
        from h2o.estimators import H2OAutoML
        aml = H2OAutoML(max_models=10, seed=1)
        aml.train(
            x=[col for col in train.columns if col != 'weight'],
            y='weight',
            training_frame=train
        )
        
        # Save model
        self.models['relationship_inference'] = aml.leader
        model_path = h2o.save_model(
            model=aml.leader, 
            path="/tmp/h2o_models/relationship_inference", 
            force=True
        )
        
        print(f"Saved relationship inference model to {model_path}")
        return True
        
    def _get_node_features(self):
        """Get node features from Neo4j"""
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (n)
                RETURN n.id as node_id,
                       n.type as node_type,
                       n.created as created,
                       size((n)--()) as degree
            """)
            
            nodes = [record.data() for record in result]
            
        # Convert to pandas DataFrame
        df = pd.DataFrame(nodes)
        
        # Add derived features
        df['age_days'] = (time.time() - df['created']) / 86400
        
        return df
        
    def forecast_time_series(self, collection, horizon_hours=24):
        """Forecast time-series data for a collection"""
        model_key = f'timeseries_{collection}'
        if model_key not in self.models:
            return None
            
        # Create future timestamps
        future_times = []
        current_time = datetime.now()
        for i in range(horizon_hours):
            future_time = current_time + timedelta(hours=i)
            future_times.append(future_time)
            
        # Convert to H2O frame
        future_df = pd.DataFrame({'timestamp': future_times})
        future = h2o.H2OFrame(future_df)
        
        # Make predictions
        predictions = self.models[model_key].predict(future)
        
        # Convert to pandas
        pred_df = predictions.as_data_frame()
        future_df['forecast'] = pred_df['predict'].values
        
        return future_df
        
    def infer_relationships(self, source_id, target_id):
        """Infer relationship strength between nodes"""
        if 'relationship_inference' not in self.models:
            return None
            
        # Get node features
        node_features = self._get_node_features()
        
        # Filter for source and target
        source_features = node_features[node_features['node_id'] == source_id]
        target_features = node_features[node_features['node_id'] == target_id]
        
        if source_features.empty or target_features.empty:
            return None
            
        # Combine features
        combined = pd.DataFrame({
            'source': [source_id],
            'target': [target_id],
            'relationship_type': ['inferred'],
            'created': [time.time()]
        })
        
        # Add node features
        for col in source_features.columns:
            if col != 'node_id':
                combined[col] = source_features[col].values[0]
                
        for col in target_features.columns:
            if col != 'node_id':
                combined[f"{col}_target"] = target_features[col].values[0]
                
        # Convert to H2O frame
        predict_frame = h2o.H2OFrame(combined)
        
        # Make prediction
        prediction = self.models['relationship_inference'].predict(predict_frame)
        
        # Convert to pandas
        pred_df = prediction.as_data_frame()
        strength = pred_df['predict'].values[0]
        
        return {
            'source': source_id,
            'target': target_id,
            'inferred_strength': strength
        }
        
    def start_forecasting_service(self, training_interval=86400):
        """Start the forecasting service"""
        def forecasting_loop():
            while True:
                try:
                    # Train time-series models
                    self.train_time_series_models()
                    
                    # Train relationship inference model
                    self.train_relationship_inference_model()
                    
                except Exception as e:
                    print(f"Error in forecasting service: {e}")
                    
                time.sleep(training_interval)
                
        thread = threading.Thread(target=forecasting_loop)
        thread.daemon = True
        thread.start()
```

**Benefits**:
- Advanced time-series forecasting for episodic memory
- Relationship inference for semantic networks
- Predictive analytics on memory access patterns
- Anomaly detection in temporal data

### Tier 5-7: Core Identity, Emotional Memory, and Collective Memory

**H2O.ai Enhancement**: Feature engineering across multi-modal data and explainable AI

```python
# /usr/local/lib/nova/tier5_7_feature_engineering.py
import h2o
import neo4j
import pymongo
import weaviate
import pandas as pd
import numpy as np
import time
import threading
import json

class Tier5_7_FeatureEngineering:
    def __init__(self):
        self.neo4j_driver = neo4j.GraphDatabase.driver(
            "bolt://localhost:7687", 
            auth=("neo4j", "password")
        )
        self.mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.weaviate_client = weaviate.Client("http://localhost:8080")
        h2o.init()
        
    def extract_multi_modal_features(self):
        """Extract features from multiple data sources"""
        # Get graph features from Neo4j
        graph_features = self._extract_graph_features()
        
        # Get vector features from Weaviate
        vector_features = self._extract_vector_features()
        
        # Get document features from MongoDB
        document_features = self._extract_document_features()
        
        # Combine features
        combined_features = self._combine_features(
            graph_features, 
            vector_features, 
            document_features
        )
        
        return combined_features
        
    def _extract_graph_features(self):
        """Extract features from Neo4j graph"""
        with self.neo4j_driver.session() as session:
            # Get node centrality metrics
            result = session.run("""
                CALL gds.pageRank.stream('nova_graph')
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).id AS node_id, score AS pagerank
            """)
            
            pagerank = {record['node_id']: record['pagerank'] for record in result}
            
            # Get community detection
            result = session.run("""
                CALL gds.louvain.stream('nova_graph')
                YIELD nodeId, communityId
                RETURN gds.util.asNode(nodeId).id AS node_id, communityId
            """)
            
            community = {record['node_id']: record['communityId'] for record in result}
            
            # Get node properties
            result = session.run("""
                MATCH (n)
                RETURN n.id as node_id, n.type as node_type, n.created as created
            """)
            
            nodes = [record.data() for record in result]
            
        # Convert to pandas DataFrame
        df = pd.DataFrame(nodes)
        
        # Add graph metrics
        df['pagerank'] = df['node_id'].map(pagerank)
        df['community'] = df['node_id'].map(community)
        
        return df
        
    def _extract_vector_features(self):
        """Extract features from Weaviate vectors"""
        # Get vector metadata
        result = self.weaviate_client.query.get(
            "Vector", 
            ["id", "class", "dimension", "creationTime"]
        ).do()
        
        if result and 'data' in result and 'Get' in result['data']:
            vectors = result['data']['Get']['Vector']
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(vectors)
            
            # Add vector similarity features
            # This would require additional processing to compute similarities
            
            return df
            
        return pd.DataFrame()
        
    def _extract_document_features(self):
        """Extract features from MongoDB documents"""
        # Get document metadata from various collections
        features = []
        
        db = self.mongo_client['nova_memory']
        collections = db.list_collection_names()
        
        for collection in collections:
            # Get document metadata
            pipeline = [
                {"$project": {"_id": 1, "created": 1, "type": 1, "tags": 1}},
                {"$limit": 1000}
            ]
            
            docs = list(db[collection].aggregate(pipeline))
            
            for doc in docs:
                doc['collection'] = collection
                features.append(doc)
                
        # Convert to pandas DataFrame
        if features:
            df = pd.DataFrame(features)
            return df
            
        return pd.DataFrame()
        
    def _combine_features(self, graph_df, vector_df, document_df):
        """Combine features from different sources"""
        # This is a simplified example - in practice, you would need
        # to define a common key to join these dataframes
        
        # For demonstration, we'll create a combined feature set
        # based on entity IDs that might be common across sources
        
        combined_features = {}
        
        # Process graph features
        if not graph_df.empty:
            for _, row in graph_df.iterrows():
                entity_id = row['node_id']
                if entity_id not in combined_features:
                    combined_features[entity_id] = {}
                    
                # Add graph features
                combined_features[entity_id].update({
                    'pagerank': row.get('pagerank'),
                    'community': row.get('community'),
                    'node_type': row.get('node_type')
                })
                
        # Process vector features
        if not vector_df.empty:
            for _, row in vector_df.iterrows():
                entity_id = row['id']
                if entity_id not in combined_features:
                    combined_features[entity_id] = {}
                    
                # Add vector features
                combined_features[entity_id].update({
                    'vector_class': row.get('class'),
                    'vector_dimension': row.get('dimension')
                })
                
        # Process document features
        if not document_df.empty:
            for _, row in document_df.iterrows():
                entity_id = str(row['_id'])
                if entity_id not in combined_features:
                    combined_features[entity_id] = {}
                    
                # Add document features
                combined_features[entity_id].update({
                    'document_collection': row.get('collection'),
                    'document_type': row.get('type')
                })
                
        # Convert to DataFrame
        combined_df = pd.DataFrame.from_dict(combined_features, orient='index')
        combined_df['entity_id'] = combined_df.index
        combined_df.reset_index(drop=True, inplace=True)
        
        return combined_df
        
    def train_explainable_model(self, target_variable):
        """Train an explainable model using multi-modal features"""
        # Extract features
        features_df = self.extract_multi_modal_features()
        
        if features_df.empty:
            return None
            
        # Get target variable (this would come from Nova feedback)
        # For demonstration, we'll simulate a target
        if target_variable == 'importance':
            features_df['importance'] = np.random.random(size=len(features_df))
        elif target_variable == 'emotional_response':
            features_df['emotional_response'] = np.random.normal(size=len(features_df))
        else:
            return None
            
        # Convert to H2O frame
        train = h2o.H2OFrame(features_df)
        
        # Train explainable model
        from h2o.estimators import H2OExplainableMlModel
        model = H2OExplainableMlModel(seed=1)
        
        x_cols = [col for col in train.columns if col != target_variable and col != 'entity_id']
        model.train(x=x_cols, y=target_variable, training_frame=train)
        
        # Get explanations
        explanations = model.explain(train)
        
        # Save model
        model_path = h2o.save_model(
            model=model, 
            path=f"/tmp/h2o_models/explainable_{target_variable}", 
            force=True
        )
        
        print(f"Saved explainable model for {target_variable} to {model_path}")
        
        return {
            'model': model,
            'explanations': explanations,
            'model_path': model_path
        }
        
    def get_feature_importance(self, model_result):
        """Get feature importance from model"""
        if not model_result or 'model' not in model_result:
            return None
            
        model = model_result['model']
        
        # Get variable importance
        varimp = model.varimp(use_pandas=True)
        
        return varimp
        
    def explain_prediction(self, model_result, entity_id):
        """Explain prediction for a specific entity"""
        if not model_result or 'model' not in model_result:
            return None
            
        # Extract features for the entity
        features_df = self.extract_multi_modal_features()
        
        if entity_id not in features_df['entity_id'].values:
            return None
            
        # Filter for the entity
        entity_features = features_df[features_df['entity_id'] == entity_id]
        
        # Convert to H2O frame
        predict_frame = h2o.H2OFrame(entity_features)
        
        # Get prediction
        model = model_result['model']
        prediction = model.predict(predict_frame)
        
        # Get SHAP values for explanation
        shap_values = model.shap_values(predict_frame)
        
        # Format explanation
        explanation = {
            'prediction': prediction.as_data_frame()['predict'].values[0],
            'shap_values': {
                col: shap_values[col][0] 
                for col in shap_values.columns
            }
        }
        
        return explanation
```

**Benefits**:
- Cross-database feature engineering
- Explainable AI for Nova reasoning
- Multi-modal data integration
- Transparent decision-making for Nova agents

## Nova Agent Integration

### H2O Wave Dashboards for Nova Agents

```python
# /usr/local/lib/nova/h2o_wave_dashboards.py
from h2o_wave import main, app, Q, ui, data
import pandas as pd
import numpy as np
import json
import time
import redis
import pymongo
import neo4j

@app('/')
async def serve(q: Q):
    if not q.client.initialized:
        initialize_page(q)
        q.client.initialized = True
        
    # Handle navigation
    if q.args.nav:
        q.page['meta'].side_panel = True
        handle_navigation(q)
        
    await q.page.save()
    
def initialize_page(q: Q):
    """Initialize the dashboard page"""
    q.page['meta'] = ui.meta_card(
        box='',
        title='Nova Agent Dashboard',
        theme='h2o-dark',
        layouts=[
            ui.layout(
                breakpoint='xs',
                width='1200px',
                zones=[
                    ui.zone('header', size='76px'),
                    ui.zone('navigation', size='80px'),
                    ui.zone('content', zones=[
                        ui.zone('main', size='1fr'),
                        ui.zone('right', size='400px')
                    ]),
                    ui.zone('footer', size='0')
                ]
            )
        ]
    )
    
    q.page['header'] = ui.header_card(
        box='header',
        title='Nova Agent Dashboard',
        subtitle='Powered by H2O.ai',
        icon='Brain',
        items=[
            ui.button(name='refresh', icon='Refresh', label='Refresh'),
            ui.button(name='settings', icon='Settings', label='Settings')
        ]
    )
    
    q.page['navigation'] = ui.tab_card(
        box='navigation',
        items=[
            ui.tab(name='nav_memory', label='Memory Tiers'),
            ui.tab(name='nav_models', label='ML Models'),
            ui.tab(name='nav_performance', label='Performance'),
            ui.tab(name='nav_explain', label='Explainability')
        ],
        value='nav_memory'
    )
    
    # Default to memory tiers view
    show_memory_tiers(q)
    
def handle_navigation(q: Q):
    """Handle navigation between dashboard sections"""
    nav = q.args.nav
    
    # Clear content area
    for key in list(q.page.keys()):
        if key.startswith('content_'):
            del q.page[key]
            
    # Show appropriate content
    if nav == 'nav_memory':
        show_memory_tiers(q)
    elif nav == 'nav_models':
        show_ml_models(q)
    elif nav == 'nav_performance':
        show_performance(q)
    elif nav == 'nav_explain':
        show_explainability(q)
        
def show_memory_tiers(q: Q):
    """Show memory tiers dashboard"""
    # Memory tier stats
    q.page['content_memory_stats'] = ui.form_card(
        box=ui.box('main', height='150px'),
        title='Memory Tier Statistics',
        items=[
            ui.stats(
                items=[
                    ui.stat(label='Tier 1 (Redis/Qdrant)', value='1.2M', caption='objects'),
                    ui.stat(label='Tier 2 (Weaviate/FAISS)', value='3.5M', caption='vectors'),
                    ui.stat(label='Tier 3-4 (MongoDB/Neo4j)', value='8.7M', caption='documents'),
                    ui.stat(label='Tier 5-7 (Core/Emotional)', value='2.3M', caption='entities')
                ]
            )
        ]
    )
    
    # Memory access patterns
    memory_data = generate_memory_access_data()
    q.page['content_memory_access'] = ui.plot_card(
        box=ui.box('main', height='300px'),
        title='Memory Access Patterns',
        data=data('tier time count', memory_data),
        plot=ui.plot([
            ui.mark(type='line', x='time', y='count', color='tier', y_min=0)
        ])
    )
    
    # Memory tier health
    q.page['content_memory_health'] = ui.form_card(
        box=ui.box('main', height='250px'),
        title='Memory Tier Health',
        items=[
            ui.progress_table(
                names=['Tier', 'Status', 'Load', 'Latency', 'Health'],
                widths=['30%', '20%', '20%', '15%', '15%'],
                rows=[
                    ui.progress_table_row(
                        'Tier 1 (Redis/Qdrant)', 
                        'Online', 
                        ui.progress(0.65), 
                        '0.5ms', 
                        ui.progress(0.95, color='$green')
                    ),
                    ui.progress_table_row(
                        'Tier 2 (Weaviate/FAISS)', 
                        'Online', 
                        ui.progress(0.78), 
                        '5.2ms', 
                        ui.progress(0.92, color='$green')
                    ),
                    ui.progress_table_row(
                        'Tier 3-4 (MongoDB/Neo4j)', 
                        'Online', 
                        ui.progress(0.45), 
                        '12.8ms', 
                        ui.progress(0.97, color='$green')
                    ),
                    ui.progress_table_row(
                        'Tier 5-7 (Core/Emotional)', 
                        'Online', 
                        ui.progress(0.35), 
                        '8.3ms', 
                        ui.progress(0.99, color='$green')
                    )
                ]
            )
        ]
    )
    
    # Recent memory operations
    q.page['content_recent_ops'] = ui.markdown_card(
        box=ui.box('right', height='700px'),
        title='Recent Memory Operations',
        content='''
        ### Tier 1 (Redis/Qdrant)
        - SET nova:context:12345 (2s ago)
        - GET nova:vector:78901 (5s ago)
        - EXPIRE nova:temp:45678 (10s ago)
        
        ### Tier 2 (Weaviate/FAISS)
        - Vector search: similarity=0.92 (3s ago)
        - Add embedding: id=v-12345 (15s ago)
        - Update metadata: id=v-78901 (30s ago)
        
        ### Tier 3-4 (MongoDB/Neo4j)
        - Query: episodic memory #45678 (8s ago)
        - Create relationship: KNOWS (12s ago)
        - Update document: id=doc-12345 (25s ago)
        
        ### Tier 5-7 (Core/Emotional)
        - Update emotional state: id=nova-001 (5s ago)
        - Query identity graph (18s ago)
        - Update collective memory (45s ago)
        '''
    )
    
def show_ml_models(q: Q):
    """Show ML models dashboard"""
    # Model inventory
    q.page['content_model_inventory'] = ui.form_card(
        box=ui.box('main', height='300px'),
        title='Model Inventory',
        items=[
            ui.table(
                columns=[
                    ui.table_column('Model', 'Model'),
                    ui.table_column('Type', 'Type'),
                    ui.table_column('Accuracy', 'Accuracy'),
                    ui.table_column('Last Updated', 'Last Updated'),
                    ui.table_column('Status', 'Status')
                ],
                rows=[
                    ui.table_row(
                        'vector_prioritization', 
                        'Random Forest', 
                        '92.5%', 
                        '10 minutes ago',
                        ui.tag(label='Active', color='$green')
                    ),
                    ui.table_row(
                        'time_series_forecast', 
                        'ARIMA+XGBoost', 
                        '88.7%', 
                        '1 hour ago',
                        ui.tag(label='Active', color='$green')
                    ),
                    ui.table_row(
                        'relationship_inference', 
                        'GNN', 
                        '90.2%', 
                        '3 hours ago',
                        ui.tag(label='Active', color='$green')
                    ),
                    ui.table_row(
                        'emotional_response', 
                        'Explainable ML', 
                        '85.3%', 
                        '6 hours ago',
                        ui.tag(label='Training', color='$yellow')
                    )
                ]
            )
        ]
    )
    
    # Model performance
    model_data = generate_model_performance_data()
    q.page['content_model_performance'] = ui.plot_card(
        box=ui.box('main', height='300px'),
        title='Model Performance Over Time',
        data=data('model time accuracy', model_data),
        plot=ui.plot([
            ui.mark(type='line', x='time', y='accuracy', color='model', y_min=0.7, y_max=1.0)
        ])
    )
    
    # Feature importance
    q.page['content_feature_importance'] = ui.plot_card(
        box=ui.box('right', height='350px'),
        title='Feature Importance (vector_prioritization)',
        data=data('feature importance', [
            ('access_frequency', 0.35),
            ('recency', 0.25),
            ('vector_dimension', 0.15),
            ('creation_time', 0.12),
            ('embedding_norm', 0.08),
            ('other', 0.05)
        ]),
        plot=ui.plot([
            ui.mark(type='interval', x='feature', y='importance', color='feature')
        ])
    )
    
    # Recent predictions
    q.page['content_recent_predictions'] = ui.markdown_card(
        box=ui.box('right', height='350px'),
        title='Recent Predictions',
        content='''
        ### vector_prioritization
        - Vector v-12345: priority=0.92 (2s ago)
        - Vector v-67890: priority=0.45 (5s ago)
        - Vector v-24680: priority=0.78 (10s ago)
        
        ### time_series_forecast
        - Collection 'agent_activity': +15% in next 24h
        - Collection 'memory_access': peak at 14:00 UTC
        - Collection 'query_latency': stable trend
        
        ### relationship_inference
        - Nodes n1->n2: strength=0.85, confidence=0.92
        - Nodes n3->n4: strength=0.32, confidence=0.88
        - Nodes n5->n6: strength=0.67, confidence=0.95
        '''
    )
    
def show_performance(q: Q):
    """Show performance dashboard"""
    # Performance overview
    q.page['content_performance_overview'] = ui.form_card(
        box=ui.box('main', height='150px'),
        title='Performance Overview',
        items=[
            ui.stats(
                items=[
                    ui.stat(label='Avg Query Latency', value='8.3ms', caption='-12% vs baseline'),
                    ui.stat(label='Throughput', value='1,250 qps', caption='+18% vs baseline'),
                    ui.stat(label='Cache Hit Rate', value='92.5%', caption='+8% vs baseline'),
                    ui.stat(label='Prediction Accuracy', value='91.2%', caption='+5% vs baseline')
                ]
            )
        ]
    )
    
    # Latency breakdown
    latency_data = generate_latency_data()
    q.page['content_latency_breakdown'] = ui.plot_card(
        box=ui.box('main', height='300px'),
        title='Latency Breakdown by Database',
        data=data('database operation latency', latency_data),
        plot=ui.plot([
            ui.mark(type='interval', x='database', y='latency', color='operation', stack='stack')
        ])
    )
    
    # Throughput over time
    throughput_data = generate_throughput_data()
    q.page['content_throughput'] = ui.plot_card(
        box=ui.box('main', height='300px'),
        title='Throughput Over Time',
        data=data('time throughput', throughput_data),
        plot=ui.plot([
            ui.mark(type='area', x='time', y='throughput', color='$blue')
        ])
    )
    
    # Optimization recommendations
    q.page['content_recommendations'] = ui.markdown_card(
        box=ui.box('right', height='700px'),
        title='AI-Generated Optimization Recommendations',
        content='''
        ### Redis (Tier 1)
        - **High Priority**: Increase maxmemory to 32GB
        - **Medium Priority**: Enable compression for values > 1KB
        - **Low Priority**: Adjust eviction policy to volatile-ttl
        
        ### Weaviate (Tier 2)
        - **High Priority**: Increase vector cache to 16GB
        - **Medium Priority**: Optimize index with 16 clusters
        - **Low Priority**: Adjust batch size for vector operations
        
        ### MongoDB (Tier 3)
        - **High Priority**: Add index on timestamp field
        - **Medium Priority**: Increase WiredTiger cache size
        - **Low Priority**: Enable zstd compression
        
        ### Neo4j (Tier 4)
        - **High Priority**: Increase heap size to 24GB
        - **Medium Priority**: Add index on relationship type
        - **Low Priority**: Optimize query cache size
        
        ### JanusGraph (Tier 5)
        - **High Priority**: Optimize vertex cache size
        - **Medium Priority**: Add composite index for identity properties
        - **Low Priority**: Adjust batch loading configuration
        
        ### ScyllaDB (Tier 5)
        - **High Priority**: Increase commitlog space
        - **Medium Priority**: Optimize compaction strategy
        - **Low Priority**: Adjust read/write consistency levels
        '''
    )
    
def show_explainability(q: Q):
    """Show explainability dashboard"""
    # Decision explanation
    q.page['content_decision_explanation'] = ui.form_card(
        box=ui.box('main', height='400px'),
        title='Decision Explanation',
        items=[
            ui.text('Select a decision to explain:'),
            ui.dropdown(
                name='decision_selector',
                value='vector_priority_12345',
                choices=[
                    ui.choice('vector_priority_12345', 'Vector Priority Decision (v-12345)'),
                    ui.choice('relationship_inference_78901', 'Relationship Inference (r-78901)'),
                    ui.choice('emotional_response_45678', 'Emotional Response (e-45678)')
                ]
            ),
            ui.text_xl('Decision: High Priority (0.92) for Vector v-12345'),
            ui.text('This vector was classified as high priority based on the following factors:'),
            ui.visualization(
                plot=ui.plot([
                    ui.mark(type='interval', x='factor', y='contribution')
                ]),
                data=data('factor contribution', [
                    ('Recent Access', 0.35),
                    ('High Query Frequency', 0.28),
                    ('Semantic Importance', 0.15),
                    ('Relationship Density', 0.12),
                    ('Vector Quality', 0.10)
                ]),
                height='250px'
            )
        ]
    )
    
    # SHAP values
    q.page['content_shap_values'] = ui.form_card(
        box=ui.box('main', height='350px'),
        title='SHAP Values for Vector Priority Model',
        items=[
            ui.text('SHAP values show how each feature contributes to pushing the model output from the base value to the model output.'),
            ui.visualization(
                plot=ui.plot([
                    ui.mark(type='interval', x='value', y='feature')
                ]),
                data=data('feature value', [
                    ('access_frequency', 0.35),
                    ('recency', 0.25),
                    ('vector_dimension', 0.15),
                    ('creation_time', -0.12),
                    ('embedding_norm', 0.08),
                    ('update_frequency', -0.05),
                    ('tag_count', 0.03),
                    ('is_cached', 0.02)
                ]),
                height='250px'
            )
        ]
    )
    
    # Model interpretability
    q.page['content_interpretability'] = ui.markdown_card(
        box=ui.box('right', height='400px'),
        title='Model Interpretability',
        content='''
        ### Global Interpretability
        
        The vector priority model makes decisions based primarily on:
        
        1. **Access patterns** (frequency and recency)
        2. **Vector characteristics** (dimension and norm)
        3. **Metadata** (tags and creation time)
        
        The model has learned that frequently accessed vectors that have been recently queried are most important to keep in fast storage.
        
        ### Rules Extracted
        
        The model can be approximated by these rules:
        
        - IF access_frequency > 0.8 AND recency < 3600 THEN priority = HIGH
        - IF access_frequency > 0.5 AND recency < 86400 THEN priority = MEDIUM
        - IF embedding_norm > 0.9 THEN priority += 0.1
        - IF vector_dimension > 1024 THEN priority += 0.05
        '''
    )
    
    # Counterfactual explanations
    q.page['content_counterfactual'] = ui.markdown_card(
        box=ui.box('right', height='350px'),
        title='Counterfactual Explanations',
        content='''
        ### What would change the decision?
        
        For Vector v-12345 (currently HIGH priority):
        
        - If access_frequency decreased from 0.9 to 0.4, priority would drop to MEDIUM
        - If recency increased from 1200s to 100000s, priority would drop to LOW
        - If both embedding_norm decreased from 0.95 to 0.7 AND vector_dimension decreased from 1536 to 768, priority would drop to MEDIUM
        
        ### Minimal Changes Required
        
        The smallest change that would alter the decision:
        
        - Decrease access_frequency by 0.3 (from 0.9 to 0.6)
        
        This insight helps Nova agents understand decision boundaries and make targeted improvements.
        '''
    )
    
def generate_memory_access_data():
    """Generate sample memory access data"""
    times = [f'{h:02d}:00' for h in range(24)]
    tiers = ['Tier 1', 'Tier 2', 'Tier 3-4', 'Tier 5-7']
    
    data = []
    for tier in tiers:
        base = np.random.randint(100, 500)
        pattern = np.sin(np.linspace(0, 2*np.pi, 24)) * 100 + base
        pattern = pattern + np.random.normal(0, 20, 24)
        
        for i, time in enumerate(times):
            data.append((tier, time, max(0, int(pattern[i]))))
            
    return data
    
def generate_model_performance_data():
    """Generate sample model performance data"""
    times = [f'Day {d}' for d in range(1, 11)]
    models = ['vector_prioritization', 'time_series_forecast', 
             'relationship_inference', 'emotional_response']
    
    data = []
    for model in models:
        base = 0.8 + np.random.random() * 0.1
        pattern = np.random.normal(0, 0.02, 10) + np.linspace(0, 0.05, 10)
        
        for i, time in enumerate(times):
            accuracy = min(0.99, max(0.7, base + pattern[i]))
            data.append((model, time, accuracy))
            
    return data
    
def generate_latency_data():
    """Generate sample latency data"""
    databases = ['Redis', 'Weaviate', 'MongoDB', 'Neo4j', 'JanusGraph', 'ScyllaDB']
    operations = ['Read', 'Write', 'Update', 'Delete']
    
    data = []
    for db in databases:
        for op in operations:
            if db == 'Redis':
                latency = np.random.uniform(0.1, 1.0)
            elif db in ['Weaviate', 'ScyllaDB']:
                latency = np.random.uniform(1.0, 5.0)
            else:
                latency = np.random.uniform(5.0, 15.0)
                
            data.append((db, op, latency))
            
    return data
    
def generate_throughput_data():
    """Generate sample throughput data"""
    times = [f'{h:02d}:00' for h in range(24)]
    
    base = 1000
    pattern = np.sin(np.linspace(0, 2*np.pi, 24)) * 500 + base
    pattern = pattern + np.random.normal(0, 100, 24)
    
    data = []
    for i, time in enumerate(times):
        data.append((time, max(0, int(pattern[i]))))
        
    return data
```

**Benefits**:
- Interactive dashboards for Nova agents
- Real-time monitoring of database performance
- Explainable AI visualizations
- Self-service analytics for Nova agents

### Nova Agent API for H2O.ai Integration

```python
# /usr/local/lib/nova/h2o_nova_api.py
from fastapi import FastAPI, HTTPException, Body
import h2o
import json
import os
import time
import threading
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

app = FastAPI(title="Nova H2O.ai API", description="API for Nova agents to interact with H2O.ai")

# Initialize H2O
h2o.init()

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nova_h2o_api")

# Model cache
model_cache = {}

@app.get("/")
async def root():
    return {"message": "Nova H2O.ai API is running"}

@app.post("/train")
async def train_model(
    model_type: str = Body(..., embed=True),
    training_data: Dict[str, List[Dict[str, Any]]] = Body(..., embed=True),
    target: str = Body(..., embed=True),
    features: List[str] = Body(..., embed=True),
    nova_id: str = Body(..., embed=True)
):
    """Train a new model for a Nova agent"""
    try:
        # Convert training data to pandas DataFrame
        df = pd.DataFrame(training_data['data'])
        
        # Convert to H2O frame
        train = h2o.H2OFrame(df)
        
        # Train model based on type
        if model_type == "automl":
            from h2o.automl import H2OAutoML
            aml = H2OAutoML(max_models=10, seed=1)
            aml.train(x=features, y=target, training_frame=train)
            model = aml.leader
        elif model_type == "gbm":
            from h2o.estimators import H2OGradientBoostingEstimator
            model = H2OGradientBoostingEstimator(seed=1)
            model.train(x=features, y=target, training_frame=train)
        elif model_type == "explainable":
            from h2o.estimators import H2OExplainableMlModel
            model = H2OExplainableMlModel(seed=1)
            model.train(x=features, y=target, training_frame=train)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported model type: {model_type}")
            
        # Save model
        model_id = f"{nova_id}_{model_type}_{int(time.time())}"
        model_path = h2o.save_model(model=model, path=f"/tmp/h2o_models/{model_id}", force=True)
        
        # Cache model
        model_cache[model_id] = model
        
        # Get model metrics
        metrics = {
            "r2": model.r2() if model.model_category == "Regression" else None,
            "mse": model.mse(),
            "rmse": model.rmse(),
            "mae": model.mae(),
            "rmsle": model.rmsle(),
            "auc": model.auc() if model.model_category == "Binomial" else None
        }
        
        return {
            "model_id": model_id,
            "model_path": model_path,
            "metrics": metrics,
            "variable_importance": model.varimp(use_pandas=True) if hasattr(model, "varimp") else None
        }
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
async def predict(
    model_id: str = Body(..., embed=True),
    data: Dict[str, List[Dict[str, Any]]] = Body(..., embed=True)
):
    """Make predictions using a trained model"""
    try:
        # Get model
        model = model_cache.get(model_id)
        
        # If not in cache, try to load from disk
        if model is None:
            try:
                model = h2o.load_model(f"/tmp/h2o_models/{model_id}")
                model_cache[model_id] = model
            except:
                raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
                
        # Convert data to pandas DataFrame
        df = pd.DataFrame(data['data'])
        
        # Convert to H2O frame
        frame = h2o.H2OFrame(df)
        
        # Make predictions
        predictions = model.predict(frame)
        
        # Convert to Python native types
        if model.model_category == "Binomial":
            result = {
                "predictions": predictions["predict"].as_data_frame()["predict"].tolist(),
                "probabilities": {
                    "0": predictions["p0"].as_data_frame()["p0"].tolist(),
                    "1": predictions["p1"].as_data_frame()["p1"].tolist()
                }
            }
        elif model.model_category == "Multinomial":
            result = {
                "predictions": predictions["predict"].as_data_frame()["predict"].tolist(),
                "probabilities": {
                    str(i): predictions[f"p{i}"].as_data_frame()[f"p{i}"].tolist()
                    for i in range(len(predictions.columns) - 1)
                }
            }
        else:
            result = {
                "predictions": predictions.as_data_frame()["predict"].tolist()
            }
            
        return result
        
    except Exception as e:
        logger.error(f"Error making predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain")
async def explain(
    model_id: str = Body(..., embed=True),
    data: Dict[str, List[Dict[str, Any]]] = Body(..., embed=True)
):
    """Get explanations for model predictions"""
    try:
        # Get model
        model = model_cache.get(model_id)
        
        # If not in cache, try to load from disk
        if model is None:
            try:
                model = h2o.load_model(f"/tmp/h2o_models/{model_id}")
                model_cache[model_id] = model
            except:
                raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
                
        # Check if model supports explanations
        if not hasattr(model, "explain"):
            raise HTTPException(status_code=400, detail="Model does not support explanations")
            
        # Convert data to pandas DataFrame
        df = pd.DataFrame(data['data'])
        
        # Convert to H2O frame
        frame = h2o.H2OFrame(df)
        
        # Get explanations
        explanations = model.explain(frame)
        
        # Format explanations
        result = {
            "shap_values": {},
            "shap_summary": {}
        }
        
        # Extract SHAP values
        for col in explanations.columns:
            if col.startswith("SHAP_"):
                feature = col.replace("SHAP_", "")
                result["shap_values"][feature] = explanations[col].as_data_frame()[col].tolist()
                
        # Get global feature importance
        if hasattr(model, "varimp"):
            varimp = model.varimp(use_pandas=True)
            if varimp is not None:
                result["feature_importance"] = varimp.to_dict(orient="records")
                
        return result
        
    except Exception as e:
        logger.error(f"Error getting explanations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export-mojo")
async def export_mojo(
    model_id: str = Body(..., embed=True),
    destination: str = Body(..., embed=True)
):
    """Export model as MOJO for deployment"""
    try:
        # Get model
        model = model_cache.get(model_id)
        
        # If not in cache, try to load from disk
        if model is None:
            try:
                model = h2o.load_model(f"/tmp/h2o_models/{model_id}")
                model_cache[model_id] = model
            except:
                raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
                
        # Check if model supports MOJO export
        if not hasattr(model, "download_mojo"):
            raise HTTPException(status_code=400, detail="Model does not support MOJO export")
            
        # Export MOJO
        mojo_path = model.download_mojo(path=destination)
        
        return {
            "model_id": model_id,
            "mojo_path": mojo_path,
            "size_bytes": os.path.getsize(mojo_path)
        }
        
    except Exception as e:
        logger.error(f"Error exporting MOJO: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/time-series-forecast")
async def time_series_forecast(
    data: Dict[str, List[Dict[str, Any]]] = Body(..., embed=True),
    time_column: str = Body(..., embed=True),
    value_column: str = Body(..., embed=True),
    horizon: int = Body(..., embed=True)
):
    """Generate time-series forecasts"""
    try:
        # Convert data to pandas DataFrame
        df = pd.DataFrame(data['data'])
        
        # Convert time column to datetime
        df[time_column] = pd.to_datetime(df[time_column])
        df = df.sort_values(time_column)
        
        # Set time column as index
        df = df.set_index(time_column)
        
        # Convert to H2O frame
        train = h2o.H2OFrame(df.reset_index())
        
        # Train time-series model
        from h2o.estimators import H2OAutoML
        aml = H2OAutoML(max_models=10, seed=1)
        aml.train(x=[time_column], y=value_column, training_frame=train)
        
        # Generate future timestamps
        last_time = df.index.max()
        future_times = []
        
        # Determine time frequency
        if len(df) >= 2:
            freq = pd.infer_freq(df.index)
            if freq is None:
                # Default to daily if frequency can't be inferred
                freq = 'D'
        else:
            freq = 'D'
            
        # Generate future timestamps
        future_index = pd.date_range(start=last_time, periods=horizon+1, freq=freq)[1:]
        future_df = pd.DataFrame(index=future_index)
        future_df[time_column] = future_df.index
        
        # Convert to H2O frame
