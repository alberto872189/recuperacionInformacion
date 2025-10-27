import sys

qrels_file = 'qrels.txt'
results_file = 'results.txt'
output_file = 'output.txt'

def read_qrels_file():
    file = open(qrels_file)
    lines = file.readlines()
    file.close()

    qrels = {}
    for line in lines:
        collapsed_line = ' '.join(line.split())
        numbers = collapsed_line.split(' ')
        if numbers[0] not in qrels:
                qrels[numbers[0]] = {}
        qrels[numbers[0]][numbers[1]] = numbers[2]

    return qrels

def read_results_file():
    file = open(results_file)
    lines = file.readlines()
    file.close()

    results = []
    for line in lines:
        collapsed_line = ' '.join(line.split())
        numbers = collapsed_line.split(' ')
        results.append(numbers)
    
    return results

def get_positives_negatives(qrels, results, k = -1):
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    iterations = 1
    for result in results:
        if (qrels[result] == '1'):
            tp += 1
        else:
            fp += 1

        if (k != -1):
            if iterations >= k:
                break
        iterations += 1
        
    iterations = 1
    results_k = results[:k] if k != -1 else results
    for key in list(qrels.keys()):
        if key not in results_k:
            if qrels[key] == '1':
                fn += 1
            else:
                tn += 1

    return [tp, tn, fp, fn]


def print_measures(qrels, results):
    total_recall = 0
    total_avg_precision = 0
    total_precision = 0
    total_precision10 = 0
    total_precision_for_interpolated = [0] * 11
    n_consultas = 0
    
    recalls = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    for key in list(qrels.keys()):
        need_number = key
        this_qrels = qrels[key]
        this_results = [value[1] for value in results if value[0] == key]
        [tp, tn, fp, fn] = get_positives_negatives(this_qrels, this_results)
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        [tp10, tn10, fp10, fn10] = get_positives_negatives(this_qrels, this_results, 10)
        precision10 = tp10 / (tp10 + fp10)

        f1 = 2 * precision * recall / (precision + recall)

        avg_precision = 0
        iteration = 1
        n_relevants = 0
        recall_precision = []
        for key in list(this_qrels.keys()):
            if this_qrels[key] == '1' and key in this_results:
                [tpk, tnk, fpk, fnk] = get_positives_negatives(this_qrels, this_results, iteration)
                precisionk = tpk / (tpk + fpk)
                recallk = tpk / (tpk + fnk)
                recall_precision.append([recallk, precisionk])
                avg_precision += precisionk
                n_relevants += 1
            iteration += 1
        if n_relevants > 0:
            avg_precision /= n_relevants

        interpolated_recall_precision = []
        iteration = 0
        for rec in recalls:
            precisions = [value[1] for value in recall_precision if value[0] >= rec]
            max_precision = max(precisions) if len(precisions) > 0 else 0
            interpolated_recall_precision.append([rec, max_precision])
            total_precision_for_interpolated[iteration] += max_precision
            iteration += 1

        print('INFORMATION NEED', need_number)
        print('precision', '{:.3f}'.format(precision))
        print('recall', '{:.3f}'.format(recall))
        print('F1', '{:.3f}'.format(f1))
        print('prec@10', '{:.3f}'.format(precision10))
        print('average_precision', '{:.3f}'.format(avg_precision))
        print('recall_precision')
        for element in recall_precision:
            print('{:.3f} {:.3f}'.format(element[0], element[1]))
        print('interpolated_recall_precision')
        for element in interpolated_recall_precision:
            print('{:.3f} {:.3f}'.format(element[0], element[1]))
        print()
        if output_file:
            with open(output_file, 'a', encoding='utf-8') as out:
                print('INFORMATION NEED', need_number, file=out)
                print('precision', '{:.3f}'.format(precision), file=out)
                print('recall', '{:.3f}'.format(recall), file=out)
                print('F1', '{:.3f}'.format(f1), file=out)
                print('prec@10', '{:.3f}'.format(precision10), file=out)
                print('average_precision', '{:.3f}'.format(avg_precision), file=out)
                print('recall_precision', file=out)
                for element in recall_precision:
                    print('{:.3f} {:.3f}'.format(element[0], element[1]), file=out)
                print('interpolated_recall_precision', file=out)
                for element in interpolated_recall_precision:
                    print('{:.3f} {:.3f}'.format(element[0], element[1]), file=out)
                print(file=out)
        total_precision += precision
        total_recall += recall
        total_precision10 += precision10
        total_avg_precision += avg_precision
        n_consultas += 1


    
    total_f1 = 2 * total_precision/n_consultas * total_recall/n_consultas / (total_precision/n_consultas + total_recall/n_consultas)
    print('TOTAL')
    print('precision', '{:.3f}'.format(total_precision / n_consultas))
    print('recall', '{:.3f}'.format(total_recall / n_consultas))
    print('F1', '{:.3f}'.format(total_f1))
    print('prec@10', '{:.3f}'.format(total_precision10 / n_consultas))
    print('MAP', '{:.3f}'.format(total_avg_precision / n_consultas))
    print('interpolated_recall_precision')
    for idx, element in enumerate(total_precision_for_interpolated):
        print('{:.3f} {:.3f}'.format(recalls[idx], element / n_consultas))
    
    if output_file:
        with open(output_file, 'a', encoding='utf-8') as out:
            print('TOTAL', file=out)
            print('precision', '{:.3f}'.format(total_precision / n_consultas), file=out)
            print('recall', '{:.3f}'.format(total_recall / n_consultas), file=out)
            print('F1', '{:.3f}'.format(total_f1), file=out)
            print('prec@10', '{:.3f}'.format(total_precision10 / n_consultas), file=out)
            print('MAP', '{:.3f}'.format(total_avg_precision / n_consultas), file=out)
            print('interpolated_recall_precision', file=out)
            for idx, element in enumerate(total_precision_for_interpolated):
                print('{:.3f} {:.3f}'.format(recalls[idx], element / n_consultas), file=out)
            print(file=out)

        # Gráfica de Precision-Recall
        try:
            import matplotlib.pyplot as plt
            if n_consultas > 0:
                x = recalls
                y = [element / n_consultas for element in total_precision_for_interpolated]
                plt.figure()
                plt.plot(x, y, marker='o', linestyle='-')
                plt.xlabel('Recall')
                plt.ylabel('Precision')
                plt.title('Interpolated Precision-Recall (TOTAL)')
                plt.grid(True)
                png_name = 'precision_recall_total.png'
                plt.savefig(png_name, bbox_inches='tight')
                """try:
                    plt.show()
                except Exception:
                    # entorno sin pantalla, ya hemos guardado la imagen
                    pass"""
            else:
                print('No hay consultas para graficar.')
        except Exception:
            print('matplotlib no disponible, no se puede mostrar la gráfica.')


i = 1
while i < len(sys.argv):
    if sys.argv[i] == '-qrels':
        qrels_file = sys.argv[i + 1]
        i += 1
    elif sys.argv[i] == '-results':
        results_file = sys.argv[i + 1]
        i += 1
    elif sys.argv[i] == '-output':
        output_file = sys.argv[i + 1]
        i += 1
    i += 1

qrels = read_qrels_file()
results = read_results_file()
 
print_measures(qrels, results)