# Bug

Defects in shipped behaviour — captures repro, observed result, and expected result.

## Template
```markdown
# Summary
Loading x results never loads when using filter y.

# Steps to Reproduce
1. Access portal [here](https://link.to.portal)
2. Click on thing
3. Filter for y

# Results
x results never loads, spinner keeps spinning, no feedback

# Expected Results
x results loads successfully, user is notified if there is an error

# Engineering Notes
- Error logs here
- Implementation of API here
- UI triggers filter here and loads results here
```
