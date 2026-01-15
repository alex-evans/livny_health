"""
Integration tests for the Livny Health backend.

Integration tests differ from unit tests in several key ways:

1. **Scope**: Unit tests test a single function/class in isolation.
   Integration tests verify that multiple components work together correctly.

2. **Dependencies**: Unit tests mock external dependencies.
   Integration tests use real implementations (repositories, services, etc.).

3. **Data**: Unit tests often use minimal test fixtures.
   Integration tests use realistic data scenarios to verify end-to-end behavior.

4. **Speed**: Integration tests are typically slower than unit tests.

5. **What they catch**: Integration tests catch issues like:
   - Incorrect data transformations between layers
   - Missing or incorrect service orchestration
   - Repository query issues
   - API contract violations
   - State management across multiple operations

Test organization:
- test_bff_integration.py: Tests HTTP endpoints with real services
- test_service_integration.py: Tests service layer with real repositories
- test_workflows.py: Tests complete user workflows across multiple services
"""
