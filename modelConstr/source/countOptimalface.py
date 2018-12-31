import csv
import itertools

import numpy


def main():
    print
    "calculating"
    knobs = ["eyes", "pyramid", "select"]
    budget_max = 19348.0
    budget_min = 888.0
    config_list = parseCSV(knobs)  # a list of items{config:dict,cost:float}
    optimal_counts, optimals, loss_if_not_custom = count(budget_max,
                                                         budget_min,
                                                         config_list, knobs)
    beautify_to_csv(optimal_counts, loss_if_not_custom)


def beautify_to_csv(optimal_counts, loss_if_not_custom):
    output = open('count.csv', 'w')
    output.write('Budget,Optimal Configs,mean,max,std\n')
    for i in range(len(optimal_counts)):
        output.write(str(i))
        output.write(',')
        output.write(str(optimal_counts[i]) + "," + str(
            loss_if_not_custom[i]['mean']) + "," + str(
            loss_if_not_custom[i]['max']) + "," + str(
            loss_if_not_custom[i]['std']))
        output.write('\n')
    output.close()


def count(budget_max, budget_min, config_list, knobs):
    budget_list = numpy.arange(budget_min + 0.1, budget_max + 1,
                               (budget_max - budget_min) / (20.0 - 1.0))
    priority_list = numpy.arange(1, 20, 1)
    print
    budget_list
    priorities = {}
    # iterate through budget list
    result = []
    result_config = []
    loss_if_not_custom = []
    for budget in budget_list:
        print
        budget
        optimals = []
        # set up the default priority list
        default_priorities_list = {}
        for knob in knobs:
            default_priorities_list[knob] = 1
        # iterate through priorities
        priorities_list = list(
            itertools.product(priority_list, repeat=len(knobs)))
        cur_loss_if_not_custom = []
        # get the optimal config using default priority
        default_config, default_qos = optimal(budget, config_list,
                                              default_priorities_list)
        print
        default_config
        for cur_priorities in priorities_list:
            # generate the priority map
            for i in range(len(cur_priorities)):
                priorities[knobs[i]] = cur_priorities[i]
            optimal_config, custom_qos = optimal(budget, config_list,
                                                 priorities)
            # nfig in optimal_configs:
            if optimal_config['config_name'] not in optimals:
                optimals.append(optimal_config['config_name'])
            # get the default config qos if applying custom QoS priority
            default_custom_qos = qos(default_config['config_map'], priorities)
            cur_loss_if_not_custom.append(
                (custom_qos - default_custom_qos) / default_custom_qos)
            # if optimal_config['config_name']!= default_config['config_name']:
            #    print priorities,optimal_config['config_name'],custom_qos, default_config['config_name'],default_custom_qos
        # print optimals
        loss_if_not_custom.append({'max': numpy.max(cur_loss_if_not_custom),
                                   'mean': numpy.mean(cur_loss_if_not_custom),
                                   'std': numpy.std(cur_loss_if_not_custom)})
        result.append(len(optimals))
        result_config.append(optimals)
    return result, result_config, loss_if_not_custom


def optimal(budget, config_list, priorities):
    configuration = None
    highest_qos = 0.0
    for config in config_list:
        if config['cost'] <= budget:
            cur_qos = qos(config['config_map'], priorities)
            if cur_qos >= highest_qos:
                highest_qos = cur_qos
                configuration = config
    return configuration, highest_qos


def qos(config_map, priorities):
    qos = 0.0
    normalized_total = 0
    for item, value in priorities.items():
        normalized_total += value
    for name, value in config_map.items():
        if name == "eyes":
            qos += (float(value) - 1) * 0.5 * priorities[
                name] / normalized_total
        elif name == "pyramid":
            qos += float(value) / 20 * priorities[name] / normalized_total
        elif name == "select":
            qos += float(value + 1) / 9 * priorities[name] / normalized_total
    return qos


def parseCSV(knobs):
    with open(
            "/home/liuliu/Research/rapidlib-linux/modelConstr/data/facePort/facts/fact_tx_cont.csv") as nav_csv:
        csv_reader = csv.reader(nav_csv, delimiter=",")
        config_list = []
        for row in csv_reader:
            configuration = ""
            config_map = {}
            cost = 0.0
            cur_knob = ""
            for item in row:
                if item in knobs:  # this is a knob
                    configuration += item
                    config_map[item] = 0
                    cur_knob = item
                else:
                    try:
                        int(item)
                        configuration += str(item)
                        config_map[cur_knob] = float(item)
                    except ValueError:
                        cost = float(item)
            config_list.append(
                {'config_name': configuration, 'config_map': config_map,
                 'cost': cost})
        print
        config_list
        return config_list


if __name__ == '__main__':
    main()
