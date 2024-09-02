# Test-driven development
This development process “_relies on the repetition of a very short development cycle: first the developer writes an (initially failing) automated test case that defines a desired improvement or new function, 
then produces the minimum amount of code to pass that test._” 
<br>So, before actually writing any code, you should write your tests. Often the test can be taken from the original GitHub issue. 
<br>However, it is always worth considering additional use cases and writing corresponding tests.

### Writing tests
All tests should go into the tests subdirectory of the specific package. 
<br>This folder contains many current examples of tests, and we suggest looking to these for inspiration.
<br>As a general tip, you can use the search functionality in your integrated development environment (IDE) or the `git grep` 
command in a terminal to find test files in which the method is called. 
<br>If you are unsure of the best location to put your test, take your best guess, 
but note that reviewers may request that you move the test to a different location.
<br>To use git grep, you can run the following command in a terminal:
```bash
git grep "function_name("
```
This will search through all files in your repository for the text `function_name(`. 
<br>This can be a useful way to quickly locate the function in the codebase and determine the best location to add a test for it.


## Using pytest
### Test structure
Tests should be written using the pytest framework. PAIG existing test structure is mostly class-based and function-based.
<br>You can write test class like this:
```bash
class TestReallyCoolFeature:
    def test_cool_feature_aspect(self):
        pass
```
Functional style using the [pytest](https://docs.pytest.org/en/latest/) framework, which offers a richer testing framework that will facilitate testing and developing. 
<br>You can write test functions like this:
```bash
def test_really_cool_feature():
    pass
```


### Running the test suite
The tests can then be run directly inside your Git clone:
1. Go to backend/paig repository
```bash
cd backend/paig
```
2. Run the tests
```bash
sh run_unit_test.sh
```
Often it is worth running only a subset of tests first around your changes before running the entire suite (**Tip:**  we use the coverage) to find out which tests hit the lines of code you’ve modified, and then run only those).
<br>The easiest way to do this is with:
<br>Update run_unit_test.sh with the test file you want to run:
```bash
coverage run --source=.  -m pytest <test_file_path>
coverage html
```
Run the tests:
```bash
sh run_unit_test.sh
```
This will run the tests and generate an HTML report in the htmlcov directory.
<br>**Note:** Before submitting your changes in a pull request, always run the full test suite.
