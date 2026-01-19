# Performance Benchmark Thresholds

This file defines the expected performance thresholds for n8n-mcp operations.

## Critical Operations

| Operation | Expected Time | Warning Threshold | Error Threshold |
|-----------|---------------|-------------------|-----------------|
| Node Loading (per package) | <100ms | 150ms | 200ms |
| Database Query (simple) | <5ms | 10ms | 20ms |
| Search (simple word) | <10ms | 20ms | 50ms |
| Search (complex query) | <50ms | 100ms | 200ms |
| Validation (simple config) | <1ms | 2ms | 5ms |
| Validation (complex config) | <10ms | 20ms | 50ms |
| MCP Tool Execution | <50ms | 100ms | 200ms |

## Benchmark Categories

### Node Loading Performance
- **loadPackage**: Should handle large packages efficiently
- **loadNodesFromPath**: Individual file loading should be fast
- **parsePackageJson**: JSON parsing overhead should be minimal

### Database Query Performance
- **getNodeByType**: Direct lookups should be instant
- **searchNodes**: Full-text search should scale well
- **getAllNodes**: Pagination should prevent performance issues

### Search Operations
- **OR mode**: Should handle multiple terms efficiently
- **AND mode**: More restrictive but still performant
- **FUZZY mode**: Slower but acceptable for typo tolerance

### Validation Performance
- **minimal profile**: Fastest, only required fields
- **ai-friendly profile**: Balanced performance
- **strict profile**: Comprehensive but slower

### MCP Tool Execution
- Tools should respond quickly for interactive use
- Complex operations may take longer but should remain responsive

## Regression Detection

Performance regressions are detected when:
1. Any operation exceeds its warning threshold by 10%
2. Multiple operations show degradation in the same category
3. Average performance across all benchmarks degrades by 5%

## Optimization Targets

Future optimization efforts should focus on:
1. **Search performance**: Implement FTS5 for better full-text search
2. **Caching**: Add intelligent caching for frequently accessed nodes
3. **Lazy loading**: Defer loading of large property schemas
4. **Batch operations**: Optimize bulk inserts and updates