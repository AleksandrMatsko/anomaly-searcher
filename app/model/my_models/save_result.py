import io
import csv
import typing
from river import metrics

def print_to_string(*args, **kwargs) -> str:
    with io.StringIO() as output:
        print(*args, file=output, **kwargs)
        return output.getvalue()

csv_header = [
    "name",
    "f1 (%)",
    "fp",
    "fn",
    "tp",
    "total",
]

class Record:
    def __init__(self, entity_name : str, dots_count : int, confusion_matrix : metrics.ConfusionMatrix):
        self.__entity_name = entity_name
        self.__dots_count = dots_count
        self.__confusion_matrix = confusion_matrix
        self.__f1 = metrics.F1(cm=self.__confusion_matrix, pos_val=1)

    @property
    def f1(self) -> float:
        return self.__f1.get()

    @property
    def fn(self) -> int:
        return int(self.__confusion_matrix[1][0])

    @property
    def fp(self) -> int:
        return int(self.__confusion_matrix[0][1])

    @property
    def tp(self) -> int:
        return int(self.__confusion_matrix[1][1])

    def to_csv_dict(self) -> dict:
        return {
            csv_header[0]: self.__entity_name,
            csv_header[1]: "{:.2f}".format(self.f1 * 100).replace(".", ","),
            csv_header[2]: self.fp,
            csv_header[3]: self.fn,
            csv_header[4]: self.tp,
            csv_header[5]: self.__dots_count
        }
    
def avg(vals : list) -> float:
    if len(vals) == 0:
        return 0.0
    return sum(vals) / len(vals)

class Report:
    def __init__(self,
                 stream_f : typing.TextIO | None = None):
        self.__records = []
        if stream_f is not None:
            self.__stream_writer = csv.DictWriter(stream_f, fieldnames=csv_header)
            self.__stream_writer.writeheader()


    def add_record(self, entity_name : str, dots_count : int, confusion_matrix : metrics.ConfusionMatrix):
        record = Record(entity_name=entity_name, dots_count=dots_count, confusion_matrix=confusion_matrix)
        self.__records.append(record)
        if self.__stream_writer:
            self.__stream_writer.writerow(record.to_csv_dict())

    def save_report(self, csv_file: typing.TextIO):
        writer = csv.DictWriter(csv_file, fieldnames=csv_header)
        writer.writeheader()

        for r in self.__records:
            writer.writerow(r.to_csv_dict())

    @property
    def avg_f1_score(self) -> float:
        return avg([r.f1 for r in self.__records])
    
    @property
    def avg_fn(self) -> float:
        return avg([r.fn for r in self.__records])
    
    @property
    def avg_fp(self) -> float:
        return avg([r.fp for r in self.__records])
    
    @property
    def avg_tp(self) -> float:
        return avg([r.tp for r in self.__records])
    
    def better(self, other : 'Report') -> bool:
        if len(self.__records) == 0:
            return False
        elif len(other.__records) == 0:
            return True

        if self.avg_f1_score > other.avg_f1_score:
            return True
        elif self.avg_f1_score < other.avg_f1_score:
            return False
        
        if self.avg_fp < other.avg_fp:
            return True
        elif self.avg_fp > other.avg_fp:
            return False
        
        return False
