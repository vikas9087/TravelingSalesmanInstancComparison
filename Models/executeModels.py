from Models.city import City
import gurobipy as gp
import Models.geneticAlgorithm as ga
import Models.mtzFormulation as mtz
import Models.secFormulation as sec
import Models.usingCallBacks as cb
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from tqdm import tqdm


def run(execute_sec : bool = False, execute_mtz : bool = False, execute_cb: bool = False):
    gurobi_env = gp.Env(empty=False)
    gurobi_env.setParam('MIPGap', 0.10)
    gurobi_env.setParam('OutputFlag', 0)
    generations = 100
    pop_size = 30
    number_cities = int(input('Please enter number of cities to be tested (At least 10): '))
    results = {'Cities': [] }
    if execute_sec:
        results['SEC'] = []
        results['SEC_Time'] = []
    if execute_cb:
        results['CB'] = []
        results['CB_Time'] = []
    if execute_mtz:
        results['MTZ'] = []
        results['MTZ_Time'] = []


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
            results['MTZ'].append(mtz_model.optimal_gap)
            results['MTZ_Time'].append(mtz_model.time_elapsed)
    __drawGraph(results, execute_sec=execute_sec, execute_mtz=execute_mtz, execute_cb= execute_cb)


def __drawGraph(results, execute_sec : bool = False, execute_mtz : bool = False, execute_cb: bool = False):
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Optimality Gap Distribution', 'Solving Time Distribution'))
    # Adding Gap Subplots
    if execute_sec:
        fig.add_trace(go.Box(y=results['SEC'], name='SEC', legendgroup='SEC', marker_color='red'),
                      row=1, col=1)
    if execute_cb:
        fig.add_trace(go.Box(y=results['CB'], name='CB', legendgroup='CB', marker_color='lightseagreen'),
                      row=1, col=1)
    if execute_mtz:
        fig.add_trace(go.Box(y=results['MTZ'], name='MTZ', legendgroup='MTZ', marker_color='chocolate'),
                      row=1, col=1)


    # Adding Time Subplots
    if execute_sec:
        fig.add_trace(go.Box(y=results['SEC_Time'], name='SEC', showlegend=False, legendgroup='SEC', marker_color='red'),
                      row=1, col=2)
    if execute_cb:
        fig.add_trace(go.Box(y=results['CB_Time'], name='CB', showlegend=False, legendgroup='CB', marker_color='lightseagreen'),
                      row=1, col=2)
    if execute_mtz:
        fig.add_trace(go.Box(y=results['MTZ_Time'], name='MTZ', showlegend=False, legendgroup='MTZ', marker_color='chocolate'),
            row=1, col=2)

    # Updating Labels
    fig.update_yaxes(title_text="Gap %", row=1, col=1)
    fig.update_yaxes(title_text="Time (seconds)", row=1, col=2)

    nr_cities = len(results['Cities'])
    max_cities = max(results['Cities'])
    fig.update_layout(title_text=f"Model Performance Comparison, Number of Instances {nr_cities}, Max Number of Cities {max_cities}", height=700)
    fig.show()
