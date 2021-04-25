from Models.city import City
import gurobipy as gp
import Models.geneticAlgorithm as ga
import Models.mtzFormulation as mtz
import Models.secFormulation as sec
import Models.usingCallBacks as cb
import matplotlib.pyplot as plt
from tqdm import tqdm


def run(execute_sec : bool = False, execute_mtz : bool = False, execute_cb: bool = False):
    gurobi_env = gp.Env(empty=False)
    gurobi_env.setParam('MIPGap', 0.10)
    gurobi_env.setParam('OutputFlag', 0)
    generations = 100
    pop_size = 30
    number_cities = int(input('Please enter number of cities to be tested (At least 10): '))
    results = {'Cities': [], 'SEC': [], 'MTZ': [], 'CB': [], 'SEC_Time': [], 'MTZ_Time': [], 'CB_Time': []}

    for i in tqdm(range(5, number_cities + 5, 5)):
        results['Cities'].append(i)
        city = City(number_cities=number_cities)
        cities = city.cities
        distance = city.pairwise_distance

        if execute_sec:
            sec_model = sec.SecModel(gurobi_env, cities, distance, None)
            sec_model.solve()
            results['SEC'].append(sec_model.optimal_gap)
            results['SEC_Time'].append(sec_model.time_elapsed)
        if execute_cb:
            cb_model = cb.CallBackModel(gurobi_env, cities, distance, startSolution=None, usingLazyConstraint=True)
            cb_model.solve()
            results['CB'].append(cb_model.optimal_gap)
            results['CB_Time'].append(cb_model.time_elapsed)
        if execute_mtz:
            start_solution = ga.solveGeneticAlgorithm(eliteSize=int(generations / 5), mutationRate=0.1,
                                                      cities=cities, popSize=pop_size, generations=generations)
            mtz_model = mtz.MtzFormulation(gurobi_env, cities, distance, startSolution=start_solution,
                                           give_initial_solution=True)
            mtz_model.solve()
            results['MTZ'].append(mtz_model.total_distance)
            results['MTZ_Time'].append(mtz_model.time_elapsed)
    __drawGraph(results)


def __drawGraph(results):
    fig, axes = plt.subplots(ncols=2, nrows=1, figsize=(12,8))
    l1, = axes[0].plot(results['Cities'], results['SEC'], ls='-')
    l2, =axes[0].plot(results['Cities'], results['CB'], ls='-.')
    # l3, =axes[0].plot(results['Cities'], results['MTZ'], ls=':')
    axes[0].set_title('Relative Optimal Gap Comparison')
    axes[0].set_xlabel('Number of Cities')
    axes[0].set_ylabel('Gap %')

    axes[1].plot(results['Cities'], results['SEC_Time'], ls='-')
    axes[1].plot(results['Cities'], results['CB_Time'], ls='-.')
    # axes[1].plot(results['Cities'], results['MTZ_Time'], ls=':')
    axes[1].set_title('Solving Time Comparison')
    axes[1].set_xlabel('Number of Cities')
    axes[1].set_ylabel('Time (seconds)')
    axes[0].legend((l1, l2), ('SEC', 'CB'), loc='best', shadow=True,fancybox=True)
    fig.tight_layout()
    fig.show()
