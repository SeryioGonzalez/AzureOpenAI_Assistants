#pydocstyle
#pylint

echo "Issues with pydocstyle:"
for python_file in $(git ls-files | egrep "*.py$")
do
    pydocstyle $python_file
done

echo "Issues with pylint:"
for python_file in $(git ls-files | egrep "*.py$")                                                                                                        
do
    pylint $python_file
done