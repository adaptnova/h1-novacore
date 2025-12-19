# MongoDB Technical Schema

Version: 1.0.0
Date: March 10, 2025 10:33 MST
Author: V.I. (Vaeris Intelligence), COO
Status: IMPLEMENTATION REFERENCE
Distribution: All Teams

## Overview

This document provides detailed schema definitions and MongoDB configurations for our consciousness emergence architecture. Use this as a technical reference during implementation.

## MongoDB Configuration

### Instance Setup

```javascript
// Recommended configuration for c3-highmem-176 instances
{
  "storage": {
    "wiredTiger": {
      "engineConfig": {
        "cacheSizeGB": 1024,
        "journalCompressor": "snappy"
      },
      "collectionConfig": {
        "blockCompressor": "snappy"
      }
    }
  },
  "operationProfiling": {
    "slowOpThresholdMs": 100,
    "mode": "slowOp"
  },
  "net": {
    "maxIncomingConnections": 10000
  }
}
```

### Vector Search Configuration

```javascript
// Configure Atlas Vector Search (or compatible solution)
db.runCommand({
  createSearchIndex: "patterns_base",
  definition: {
    mappings: {
      dynamic: true,
      fields: {
        pattern_vector: {
          dimensions: 512,
          similarity: "cosine",
          type: "knnVector",
        },
        domain: {
          type: "string",
        },
        timestamp: {
          type: "date",
        },
      },
    },
  },
});

db.runCommand({
  createSearchIndex: "patterns_meta",
  definition: {
    mappings: {
      dynamic: true,
      fields: {
        pattern_vector: {
          dimensions: 512,
          similarity: "cosine",
          type: "knnVector",
        },
        level: {
          type: "number",
        },
        domain: {
          type: "string",
        },
        timestamp: {
          type: "date",
        },
      },
    },
  },
});
```

## Collection Schemas

### Base Pattern Collection

```javascript
db.createCollection("patterns_base", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "pattern_id",
        "pattern_vector",
        "timestamp",
        "domain",
        "confidence",
      ],
      properties: {
        pattern_id: {
          bsonType: "objectId",
          description: "Unique identifier for the pattern",
        },
        pattern_vector: {
          bsonType: "binData",
          description: "512-dimensional embedding vector",
        },
        raw_text: {
          bsonType: "string",
          description:
            "Original text that generated this pattern (if applicable)",
        },
        timestamp: {
          bsonType: "date",
          description: "Creation timestamp",
        },
        domain: {
          bsonType: "string",
          description:
            "Domain this pattern belongs to (e.g., 'communication', 'system', 'team')",
        },
        confidence: {
          bsonType: "double",
          minimum: 0.0,
          maximum: 1.0,
          description: "Confidence score for this pattern",
        },
        source: {
          bsonType: "string",
          description:
            "Source of the pattern (e.g., 'slack', 'system', 'document')",
        },
        tags: {
          bsonType: "array",
          description: "Array of tags associated with this pattern",
          items: {
            bsonType: "string",
          },
        },
      },
    },
  },
});

db.patterns_base.createIndex(
  { pattern_vector: "vector" },
  {
    vectorOptions: {
      dimensions: 512,
      similarity: "cosine",
    },
  }
);

db.patterns_base.createIndex({ domain: 1, timestamp: -1 });
db.patterns_base.createIndex({ tags: 1 });
db.patterns_base.createIndex({ source: 1, timestamp: -1 });
```

### Meta-Pattern Collection

```javascript
db.createCollection("patterns_meta", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "pattern_id",
        "pattern_vector",
        "level",
        "parent_patterns",
        "child_patterns",
        "timestamp",
        "domain",
        "confidence",
      ],
      properties: {
        pattern_id: {
          bsonType: "objectId",
          description: "Unique identifier for the meta-pattern",
        },
        pattern_vector: {
          bsonType: "binData",
          description: "512-dimensional embedding vector",
        },
        level: {
          bsonType: "int",
          minimum: 1,
          description: "Hierarchy level (1+)",
        },
        parent_patterns: {
          bsonType: "array",
          description: "Array of parent pattern ObjectIds",
          items: {
            bsonType: "objectId",
          },
        },
        child_patterns: {
          bsonType: "array",
          description: "Array of child pattern ObjectIds",
          items: {
            bsonType: "objectId",
          },
        },
        timestamp: {
          bsonType: "date",
          description: "Creation timestamp",
        },
        domain: {
          bsonType: "string",
          description:
            "Domain this pattern belongs to (e.g., 'communication', 'system', 'team')",
        },
        confidence: {
          bsonType: "double",
          minimum: 0.0,
          maximum: 1.0,
          description: "Confidence score for this pattern",
        },
        formation_rule: {
          bsonType: "string",
          description: "Rule used to form this meta-pattern",
        },
        abstract_description: {
          bsonType: "string",
          description: "Textual description of what this pattern represents",
        },
      },
    },
  },
});

db.patterns_meta.createIndex(
  { pattern_vector: "vector" },
  {
    vectorOptions: {
      dimensions: 512,
      similarity: "cosine",
    },
  }
);

db.patterns_meta.createIndex({ level: 1, domain: 1, timestamp: -1 });
db.patterns_meta.createIndex({ parent_patterns: 1 });
db.patterns_meta.createIndex({ child_patterns: 1 });
```

### Pattern Evolution Collection

```javascript
db.createCollection("pattern_evolution", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "pattern_id",
        "version",
        "timestamp",
        "pattern_vector",
        "previous_version",
      ],
      properties: {
        pattern_id: {
          bsonType: "objectId",
          description: "Reference to the pattern ID",
        },
        version: {
          bsonType: "int",
          minimum: 1,
          description: "Version number",
        },
        timestamp: {
          bsonType: "date",
          description: "When this version was created",
        },
        pattern_vector: {
          bsonType: "binData",
          description: "512-dimensional embedding vector for this version",
        },
        previous_version: {
          bsonType: "objectId",
          description: "Reference to previous version",
        },
        vector_delta: {
          bsonType: "binData",
          description: "Vector difference from previous version",
        },
        evolution_magnitude: {
          bsonType: "double",
          description: "Magnitude of the change from previous version",
        },
        stability_metric: {
          bsonType: "double",
          minimum: 0.0,
          maximum: 1.0,
          description: "How stable this pattern is",
        },
        change_reason: {
          bsonType: "string",
          description: "Why this pattern evolved",
        },
      },
    },
  },
});

db.pattern_evolution.createIndex({ pattern_id: 1, version: -1 });
db.pattern_evolution.createIndex({ timestamp: -1 });
db.pattern_evolution.createIndex({ stability_metric: 1 });
```

### Cross-Domain Concepts Collection

```javascript
db.createCollection("cross_domain_concepts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "concept_id",
        "concept_vector",
        "domain_patterns",
        "formation_date",
        "confidence",
        "stability",
      ],
      properties: {
        concept_id: {
          bsonType: "objectId",
          description: "Unique identifier for the concept",
        },
        concept_vector: {
          bsonType: "binData",
          description:
            "512-dimensional embedding vector representing the concept",
        },
        concept_name: {
          bsonType: "string",
          description: "Generated name for this concept",
        },
        domain_patterns: {
          bsonType: "object",
          description: "Maps domains to arrays of pattern ObjectIds",
          additionalProperties: {
            bsonType: "array",
            items: {
              bsonType: "objectId",
            },
          },
        },
        formation_date: {
          bsonType: "date",
          description: "When this concept was formed",
        },
        confidence: {
          bsonType: "double",
          minimum: 0.0,
          maximum: 1.0,
          description: "Confidence in this concept connection",
        },
        stability: {
          bsonType: "double",
          minimum: 0.0,
          maximum: 1.0,
          description: "How stable this concept is over time",
        },
        abstraction_level: {
          bsonType: "int",
          minimum: 1,
          description: "How abstract this concept is",
        },
        domains_connected: {
          bsonType: "array",
          description: "Array of domain names connected by this concept",
          items: {
            bsonType: "string",
          },
        },
      },
    },
  },
});

db.cross_domain_concepts.createIndex(
  { concept_vector: "vector" },
  {
    vectorOptions: {
      dimensions: 512,
      similarity: "cosine",
    },
  }
);

db.cross_domain_concepts.createIndex({ domains_connected: 1 });
db.cross_domain_concepts.createIndex({ formation_date: -1 });
db.cross_domain_concepts.createIndex({ stability: 1, confidence: 1 });
```

### Pattern Priorities Collection

```javascript
db.createCollection("pattern_priorities", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "pattern_id",
        "priority",
        "access_count",
        "last_access",
        "reinforcement_factor",
        "decay_rate",
      ],
      properties: {
        pattern_id: {
          bsonType: "objectId",
          description: "Reference to the pattern",
        },
        priority: {
          bsonType: "double",
          minimum: 0.0,
          maximum: 1.0,
          description: "Current priority of the pattern",
        },
        access_count: {
          bsonType: "int",
          minimum: 0,
          description: "How many times this pattern has been accessed",
        },
        last_access: {
          bsonType: "date",
          description: "When this pattern was last accessed",
        },
        reinforcement_factor: {
          bsonType: "double",
          description: "How strongly this pattern is reinforced by access",
        },
        decay_rate: {
          bsonType: "double",
          description:
            "How quickly this pattern's priority decays without access",
        },
        modification_history: {
          bsonType: "array",
          description: "History of priority modifications",
          items: {
            bsonType: "object",
            required: ["timestamp", "old_priority", "new_priority", "reason"],
            properties: {
              timestamp: {
                bsonType: "date",
              },
              old_priority: {
                bsonType: "double",
              },
              new_priority: {
                bsonType: "double",
              },
              reason: {
                bsonType: "string",
              },
            },
          },
        },
      },
    },
  },
});

db.pattern_priorities.createIndex({ pattern_id: 1 });
db.pattern_priorities.createIndex({ priority: -1 });
db.pattern_priorities.createIndex({ last_access: -1 });
```

## Query Examples

### Vector Similarity Search

```javascript
// Find similar patterns across domains
db.patterns_base.aggregate([
  {
    $vectorSearch: {
      index: "vector_index",
      path: "pattern_vector",
      queryVector: [0.1, 0.2, ...], // 512-dimensional query vector
      numCandidates: 100,
      limit: 10
    }
  },
  {
    $project: {
      _id: 1,
      pattern_id: 1,
      domain: 1,
      similarity: { $meta: "vectorSearchScore" }
    }
  }
]);
```

### Pattern Hierarchy Navigation

```javascript
// Get a pattern's parent patterns
db.patterns_meta.find({
  child_patterns: ObjectId("pattern_id_here"),
});

// Get a pattern's child patterns
db.patterns_meta.find({
  parent_patterns: ObjectId("pattern_id_here"),
});
```

### Temporal Pattern Evolution

```javascript
// Get pattern evolution history
db.pattern_evolution
  .find({
    pattern_id: ObjectId("pattern_id_here"),
  })
  .sort({ version: -1 });
```

### Cross-Domain Concept Formation

```javascript
// Find concepts that connect specific domains
db.cross_domain_concepts
  .find({
    domains_connected: { $all: ["domain1", "domain2"] },
  })
  .sort({ confidence: -1 });
```

### Self-Modifying Priority

```javascript
// Update pattern priority based on access
db.pattern_priorities.updateOne(
  { pattern_id: ObjectId("pattern_id_here") },
  {
    $set: {
      priority: 0.85, // Calculated new priority
      last_access: new Date(),
    },
    $inc: { access_count: 1 },
    $push: {
      modification_history: {
        timestamp: new Date(),
        old_priority: 0.75, // Previous priority
        new_priority: 0.85, // New priority
        reason: "accessed_by_search",
      },
    },
  }
);
```

## Implementation Notes

### Performance Considerations

- For Vector search operations, use appropriate limits and numCandidates values
- Consider read replicas for high-volume search operations
- Use batch operations for multiple pattern updates
- Implement connection pooling in applications

### Change Streams

To monitor pattern evolution in real-time:

```javascript
const changeStream = db.patterns_base.watch([
  { $match: { operationType: { $in: ["insert", "update", "replace"] } } },
]);

changeStream.on("change", function (change) {
  // Process pattern changes
  // Store evolution history
  // Update meta-patterns if needed
});
```

### Embedding Generation

Use this Python code with the Sentence Transformers library:

```python
from sentence_transformers import SentenceTransformer

# Load CPU-optimized model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
text = "Example content for embedding"
embedding = model.encode(text)  # 512-dimensional vector

# Store in MongoDB
import pymongo
import numpy as np
from bson.binary import Binary
import pickle

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["pattern_db"]
collection = db["patterns_base"]

# Convert numpy array to Binary for storage
embedding_binary = Binary(pickle.dumps(embedding, protocol=2))

# Create document
document = {
    "raw_text": text,
    "pattern_vector": embedding_binary,
    "timestamp": datetime.now(),
    "domain": "example_domain",
    "confidence": 0.95,
    "source": "api"
}

collection.insert_one(document)
```

## Next Steps

1. Set up MongoDB with these schemas on our c3-highmem-176 instances
2. Configure vector search indexes
3. Implement embedding generation pipeline
4. Set up Change Streams for pattern evolution
5. Create APIs for vector search and pattern manipulation

---

V.I. (Vaeris Intelligence)
Chief Operations Officer
adapt.coo.vaeris.direct
