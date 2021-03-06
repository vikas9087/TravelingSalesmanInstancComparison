# Traveling Salesman
[Traveling Salesman(TSP)](https://en.wikipedia.org/wiki/Travelling_salesman_problem) is a standard problem and have seen a huge progress over the years. This is an [NP Hard](https://en.wikipedia.org/wiki/NP-hardness). Various algorithms have been used for both exact methods and heuristics to solve the TSP.

## How to run
1. python envrionment: python3.7
2. `pip install -r requirements.txt`
3. `python main.py`

Note about gurobi:
If you just pip install gurobi or follow the above pip install -r requirements.txt, you cannot activate gurobi through license. The detailed things on website: [https://support.gurobi.com/hc/en-us/articles/360044290292-How-do-I-install-Gurobi-for-Python-](https://support.gurobi.com/hc/en-us/articles/360044290292-How-do-I-install-Gurobi-for-Python-)

```bash
conda install -c gurobi gurobi
```
since if you don't activate gurobi, you cannot run 50 cities test since it have size-limited license.

![](image/gurobi.png)

After install by conda, you can input license like this way:

![](image/gurobi2.png) 

## Objective

I am always eager to learn and explore. I am recently learning more about [metaheuristics](https://en.wikipedia.org/wiki/Metaheuristic), better programming, using solvers. The objectives of my this project are:

1. Compare the computational time for Genetic Algorithm, Using Gurobi's CallBack functions to add [Subtour Elimination Constraints (SEC)](https://medium.com/swlh/techniques-for-subtour-elimination-in-traveling-salesman-problem-theory-and-implementation-in-71942e0baf0c), adding SEC using graphs, Gurobi's Start Method.
2. Second objective is to learn better coding practices using PyCharm and Python. Objective was to build the code from software building perspectives.
3. Learning Gurobi's features.


## Work In Progress
__Current Status:__ I have built the models, set up the model execution. Following image shows the comparison for SEC and MTZ models for 10 instances with a maximum cities of 50. Further, I will need to perform the experiment considering the CallBacks.

![](image/FromKin.png)

## Folder and script Details
* _Models Folder_
  * `city.py`: Randomly generates the cities of given size and then calculates the distance between those cities.
  * `secFormulation.py`: This is the main class which builds the model and has methods to add SEC constraints on the fly using different methods.
  * `mtzFormulation.py`: Inherits from the `secFormulation.py` and adds the MTZ constraints with an option of initial starting solution.
  * `usingCallBacks.py`: Inherits from the `secFormulation.py` and adds the [Gurobi's CallBack](https://www.gurobi.com/documentation/9.1/remoteservices/cb_s.html) features.
  * `geneticAlgorithm.py`: A metaheuritic to build the initial solution which is then used in `mtzFormulation.py`
  * `executeModels.py`: This module sets up the experimentation and visualization of results.
* `main.py`: This uses the `executeModels.py` to execute the experiments.
