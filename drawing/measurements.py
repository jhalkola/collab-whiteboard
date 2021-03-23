import os
import statistics

values = {
    "c2": "",
    "c2_avg": 0,
    "c2_std_div": 0,
    "c5": "",
    "c5_avg": 0,
    "c5_std_div": 0,
    "c10": "",
    "c10_avg": 0,
    "c10_std_div": 0,
    "c15": "",
    "c15_avg": 0,
    "c15_std_div": 0
}


def get_values():
    c2_values = []
    c5_values = []
    c10_values = []
    c15_values = []

    file_numbers = [2, 5, 10, 15]
    for i in file_numbers:
        try:
            path = os.listdir("log/clients{}".format(i))
        except FileNotFoundError:
            pass
        else:
            for filename in path:
                with open(os.path.join("log/clients{}".format(i), filename), "r") as f:
                    if (i == 2):
                        for value in f:
                            value = float(value.strip())
                            c2_values.append(value)
                        values["c2_avg"] = "Avg response time: {}\n".format(statistics.mean(c2_values))
                        values["c2_std_div"] = "Standard diviation: {}\n".format(statistics.stdev(c2_values))
                        values["c2"] = ["2 clients\n", values["c2_avg"], values["c2_std_div"]]
                    elif (i == 5):
                        for value in f:
                            value = float(value.strip())
                            c5_values.append(value)
                        values["c5_avg"] = "Avg response time: {}\n".format(statistics.mean(c5_values))
                        values["c5_std_div"] = "Standard diviation: {}\n".format(statistics.stdev(c5_values))
                        values["c5"] = ["\n5 clients\n", values["c5_avg"], values["c5_std_div"]]
                    elif (i == 10):
                        for value in f:
                            value = float(value.strip())
                            c10_values.append(value)
                        values["c10_avg"] = "Avg response time: {}\n".format(statistics.mean(c10_values))
                        values["c10_std_div"] = "Standard diviation: {}\n".format(statistics.stdev(c10_values))
                        values["c10"] = ["\n10 clients\n", values["c10_avg"] , values["c10_std_div"]]
                    elif (i == 15):
                        for value in f:
                            value = float(value.strip())
                            c15_values.append(value)
                        values["c15_avg"] = "Avg response time: {}\n".format(statistics.mean(c15_values))
                        values["c15_std_div"] = "Standard diviation: {}\n".format(statistics.stdev(c15_values))
                        values["c15"] = ["\n15 clients\n", values["c15_avg"] , values["c15_std_div"]]

    with open("log/outcome.txt", "w") as f:
        f.writelines(values["c2"])
        f.writelines(values["c5"])
        f.writelines(values["c10"])
        f.writelines(values["c15"])


def main():
    get_values()

if __name__ == "__main__":
    main()