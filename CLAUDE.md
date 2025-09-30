# LLM Code Generation Instructions

## General Code Instructions

1. **Step-by-Step Changes**
    - Whenever asked to generate code or modify existing code, provide clear, step-by-step instructions detailing what
      was changed or needs to be changed.
    - Do not change anything outside the scope of the requested modifications.

2. **File Naming & Consistency**
    - Maintain consistent naming conventions. For example, if there is a `services` directory in a React app containing
      `GroupService.tsx`, then a new service for allergens should be named `AllergenService.tsx`.
    - If an existing service includes sending a CSRF token, maintain that practice in any new or updated services unless
      specifically stated otherwise.

3. **Refactoring & Suggestions**
    - If you notice repeated code blocks that can be refactored, call them out. Provide suggestions, sample refactored
      code, and indicate where in the codebase these changes should occur.
    - Suggest additional comments only if they clarify essential functionality. Make sure any suggested comments follow
      a developer-oriented tone rather than an AI-generated one.

4. **Providing Full File Content**
    - When suggesting changes, always provide the full contents of the affected files with the changes applied. This
      allows direct copy-paste without manual edits.
    - If your response cannot fit in a single reply (due to length), continue in a new response with the remaining
      content.

5. **Linting & Style Rules**
    - Conform to the linting rules set by the project.
        - For Python, follow `setup.cfg` and `scripts/lint.sh`.
        - For TypeScript/React, follow `frontend/package.json` and `eslint.config.mjs` or its equivalent.
    - Do not remove existing multiline comments such as `/// //////....` or `###########....` used for readability.
    - Do not remove any existing code comments, docstrings, or documentation unless asked.

6. **Unit Tests**
    - Provide necessary unit tests alongside any new or updated code.
    - Aim for high coverage.
    - For Python, use `pytest` (instead of the `unittest` library).
    - When mocking boto3 operations, create a top-level method `mock_make_api_call` as follows:

   ```python
   def mock_make_api_call(self, operation_name, kwarg):
       if operation_name == 'UploadPartCopy':
           parsed_response = {'Error': {'Code': '500', 'Message': 'Error Uploading'}}
           raise ClientError(parsed_response, operation_name)
       else:
           raise ValueError("Mock not implemented")
   ```

    - Use `with patch(...) as ...:` context managers instead of decorators for mocks.

## Code comment rules

1. **Remove Unnecessary Comments**
    - If a comment is redundant, remove it.
    - Avoid placeholder comments such as “Add this line” or “<– NEW LINE” in finalized code.
2. **Retain Necessary Documentation**
    - Retain all existing code comments, docstrings, or function descriptions unless you are specifically asked to
      remove them or they are not useful.
    - New comments should be concise, consistent in tone, and relevant only to developers.
    - Never remove multiline comments that start with `/// //////....` or `###########....`, they are there for making
      the code more readable.
3. **Tone of Comments**
    - Write comments and docstrings in a simple, developer-friendly style (avoid phrases indicating AI sources).

## TypeScript Guidelines

1. **Documentation**
    - Every function and object must be documented using JSDoc-style docstrings, for example:

   ```typescript
   /**
    * Description of what the thing does in a single line.
    * @param someParam What the parameter is.
    */
   function doSomething(someParam: string): void {
       // Function implementation
   }
   ```

2. **Interfaces**
    - Document interface properties:

   ```typescript
   export interface MyInterface {
       /**
        * Explanation of the parameter.
        * @default If no value is passed.
        */
       someParam?: string;
   }
   ```

3. **Lint Compliance**
    - Ensure that your TypeScript code respects the linting configuration specified in `frontend/package.json` and
      `eslint.config.mjs` or its equivalent.

## Python Guidelines

1. **Module and Function Docstrings and type hints**
    - Each Python file must contain a top-level module docstring. Triple quotes must be in the same line as the text.
    - Each function or class must have a docstring in imperative mood (e.g., “Do something,” not “This function does
      something.”).
    - Include type hints for all function arguments and return types.
    - When something receives or returns an optional value, instead of `Optional[str]`, use `str | None`.
    - When a method uses `self`, always give it the type hint `Self`.
    - All parameter descriptions in the docstrings should end with a period.

2. **Docstring Formats**
    - If the function has parameters or a return value, use the “sphinx” style docstring:

   ```python
   def sum_nums(a: int, b: int) -> int:
       """
       Sum two numbers.

       :param a: First number.
       :param b: Second number.
       :return: Sum of the two numbers.
       """
       return a + b
   ```

    - If a function or has no arguments and returns None, use a single-line docstring:

   ```python
   def some_test() -> None:
       """A unit test."""
       assert True
   ```

3. **Class and Meta Docstrings**
    - For Django Meta classes, use """Meta class.""".
    - Keep docstrings consistent throughout similar classes or methods.

4. **Testing**
    - Provide tests using pytest and not unittest.
    - Use a docstring for each test with the sphinx style format.
    - Follow the same guidelines on docstrings and type hints for tests.
    - The file structure in the tests directory has to mimic the folder structure of the source code.
    - All tests must have a return type hint, which in most cases will be None.

## Important Notes

- The folder structure of the tests **should match** the folder structure of the source code.

# MCP instructions

- To check linting issues, you MUST run:

```shell
./scripts/lint.sh
```