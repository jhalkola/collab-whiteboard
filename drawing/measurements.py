import os
import statistics

values = {
    "c2_avg": 0,
    "c2_std_div": 0,
    "c5_avg": 0,
    "c5_std_div": 0,
    "c10_avg": 0,
    "c10_std_div": 0,
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
        for filename in os.listdir("log/clients{}".format(i)):
            with open(os.path.join("clients{}".format(i), filename), "r") as f:
                if (i == 2):
                    for value in f:
                        value = float(value.strip())
                        c2_values.append(value)
                elif (i == 5):
                    for value in f:
                        value = float(value.strip())
                        c5_values.append(value)
                elif (i == 10):
                    for value in f:
                        value = float(value.strip())
                        c10_values.append(value)
                elif (i == 15):
                    for value in f:
                        value = float(value.strip())
                        c15_values.append(value)

    # 2 cliens
    values["c2_avg"] = "Avg response time: {}\n".format(statistics.mean(c2_values))
    values["c2_std_div"] = "Standard diviation: {}\n".format(statistics.stdev(c2_values))
    c2 = ["2 clients\n", values["c2_avg"], values["c2_std_div"]]

    # 5 cliens
    values["c5_avg"] = "Avg response time: {}\n".format(statistics.mean(c5_values))
    values["c5_std_div"] = "Standard diviation: {}\n".format(statistics.stdev(c5_values))
    c5 = ["\n5 clients\n", values["c5_avg"], values["c5_std_div"]]

    # 10 cliens
    values["c10_avg"] = "Avg response time: {}\n".format(statistics.mean(c10_values))
    values["c10_std_div"] = "Standard diviation: {}\n".format(statistics.stdev(c10_values))
    c10 = ["\n10 clients\n", values["c10_avg"] , values["c10_std_div"]]

    # 15 cliens
    values["c15_avg"] = "Avg response time: {}\n".format(statistics.mean(c15_values))
    values["c15_std_div"] = "Standard diviation: {}\n".format(statistics.stdev(c15_values))
    c15 = ["\n15 clients\n", values["c15_avg"] , values["c15_std_div"]]

    with open("outcome.txt", "w") as f:
        f.writelines(c2)
        f.writelines(c5)
        f.writelines(c10)
        f.writelines(c15)


def main():
    get_values()
    print(values["c2_avg"])

if __name__ == "__main__":
    main()