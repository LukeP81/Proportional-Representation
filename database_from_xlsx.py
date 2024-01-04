import sqlite3

from tqdm import tqdm
import pandas as pd

# elections before 1955 have constituencies with no Votes data
MIN_ELECTION_YEAR = 1955
EXCEL_FILE_PATH = "1918-2019election_results_by_pcon.xlsx"
DATABASE_NAME = "elections.db"


def process_election_data(
        election_data: pd.DataFrame
) -> pd.DataFrame:
    """
    Clean and transform the given DataFrame

    :param election_data: The input DataFrame to be cleaned and transformed
    :type election_data: pandas.DataFrame
    :return: Cleaned and transformed DataFrame
    :rtype: pandas.DataFrame
    """

    election_data = election_data.dropna(axis=1, how="all").copy()

    # deal with merged cells
    if election_data.iloc[2, 0] != "id":
        election_data.iloc[2, 0] = "id"
    for i, column_names in enumerate(election_data.iloc[2, :]):
        clean_name = str(column_names).strip()
        if clean_name not in ["Votes", "Vote share"]:
            continue
        party_name = election_data.iloc[
            1, i if clean_name == "Votes" else i - 1]
        election_data.iloc[2, i] = f"{clean_name}-{party_name}"

    election_data.columns = election_data.iloc[2]
    election_data = election_data.iloc[3:, :].dropna(
        subset=["id"]
    ).reset_index(
        drop=True
    ).set_index(keys="id")

    return election_data


def valid_sheet(
        sheet_name: str
) -> bool:
    """
    Check if a given sheet name is valid based on specific criteria.

    :param sheet_name: The name of the sheet to be validated.
    :type sheet_name: str
    :return: True if the sheet is valid, False otherwise.
    :rtype: bool
    """

    try:
        if int(sheet_name) < MIN_ELECTION_YEAR:
            return True
    except ValueError:
        if sheet_name in ["1974F", "1974O"]:
            return True
    return False


def create_database(
        excel_file_path: str,
        database_name: str = "output.db"
) -> None:
    """
    Create a SQLite database from an Excel file

    :param excel_file_path: The path to the Excel file containing election results
    :type excel_file_path: str
    :param database_name: The name of the SQLite database to be created
    :type database_name: str
    :return: None
    :rtype: None
    """

    xls = pd.ExcelFile(path_or_buffer=excel_file_path)

    with sqlite3.connect(database=database_name) as conn:
        for sheet_name in tqdm(iterable=xls.sheet_names):
            if not valid_sheet(sheet_name):
                continue

            election_data = pd.read_excel(io=xls,
                                          sheet_name=sheet_name)
            election_data = process_election_data(election_data=election_data)
            election_data.to_sql(name=sheet_name,
                                 con=conn,
                                 index=False,
                                 if_exists="replace")


def main() -> None:
    """
    Creates a database (.db file) from an excel file containing election data.
    """

    create_database(EXCEL_FILE_PATH, DATABASE_NAME)
    print(f"Database \"{DATABASE_NAME}\" successfully created.")


if __name__ == "__main__":
    main()
