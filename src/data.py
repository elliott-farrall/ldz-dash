from __future__ import annotations

from html import unescape
from types import TracebackType
from typing import Optional

from flask_login import current_user  # type: ignore
from pandas import DataFrame, concat, read_csv, to_datetime
from pandas.errors import EmptyDataError
from werkzeug.datastructures import ImmutableMultiDict

from .settings import DATA_DIR, TEMPLATES_DIR

DATA_TEMPLATES = TEMPLATES_DIR / "data"


class Data:
    categories = {
        dir.name: [path.stem for path in dir.iterdir()]
        for dir in (DATA_TEMPLATES).iterdir()
        if dir.is_dir()
    }

    def __init__(self, category: str, subcategory: str, username: Optional[str] = None) -> None:
        self.category = category
        self.subcategory = subcategory

        if username:
            self.username = username
        else:
            self.username = current_user.username

        self.path = (DATA_DIR / self.username / category / unescape(subcategory)).with_suffix(".csv")
        if self.path.exists():
            try:
                self._table = read_csv(self.path, index_col=False)
            except EmptyDataError:
                self._table = DataFrame()
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._table = DataFrame()

        if "Date" in self._table.columns:
            self._table["Date"] = to_datetime(self._table["Date"])

    def __enter__(self) -> Data:
        return self

    def __exit__(self, exception_type: Optional[type[BaseException]], exception_value: Optional[BaseException], exception_traceback: Optional[TracebackType]) -> None:
        self._table.to_csv(self.path, index=False)

    def append(self, row: ImmutableMultiDict) -> None:
        row_dict = dict(row.lists())
        for key, values in row_dict.items():
            if len(values) > 1:
                row_dict[key] = [' | '.join(values)]

        self._table = concat([DataFrame(row_dict, index=[0]), self._table], ignore_index=True)
        self._table["Date"] = to_datetime(self._table["Date"])
        self._table.sort_values("Date", ascending=False, inplace=True)

    def __getitem__(self, idx: int) -> dict:
        return self._table.iloc[idx].to_dict()

    def __delitem__(self, idx: int) -> None:
        self._table = self._table.drop(idx)
        self._table.sort_values("Date", ascending=False, inplace=True)

    def __len__(self) -> int:
        return self._table.shape[0]

    @property
    def empty(self) -> bool:
        return self._table.empty

    @property
    def table(self) -> DataFrame:
        return self._table

    @property
    def columns(self) -> list:
        return self._table.columns.tolist()

    @property
    def values(self) -> list:
        table = self._table.copy()
        table["Date"] = table["Date"].dt.date
        return table.fillna("").values.tolist()
