import sqlite3

from tqdm import tqdm
import pandas as pd

# elections before 1955 have constituencies with no Votes data
MIN_ELECTION_YEAR = 1955


def clean_and_transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform the given DataFrame

    :param df: The input DataFrame to be cleaned and transformed
    :type df: pandas.DataFrame
    :return: Cleaned and transformed DataFrame
    :rtype: pandas.DataFrame
    """

    # remove blank rows
    df = df.dropna(axis=1, how="all").copy()

    # give correct formatting to parties (the Excel file has merged cells)
    for i, value in enumerate(df.iloc[2, :]):
        if str(value).strip() == "Votes":
            df.iloc[2, i] = f"Votes-{df.iloc[1, i]}"
        elif str(value).strip() == "Vote share":
            df.iloc[2, i] = f"Vote share-{df.iloc[1, i - 1]}"

    # 1983 onwards has a merged cell for the id
    if df.iloc[2, 0] != "id":
        df.iloc[2, 0] = "id"

    # set the column names and remove redundant rows
    df.columns = df.iloc[2]
    df = df.iloc[3:, :].dropna(subset=["id"]).reset_index(drop=True).set_index(
        "id")

    return df


def valid_sheet(sheet_name):
    try:
        if int(sheet_name) < MIN_ELECTION_YEAR:
            return True
    except ValueError:
        if sheet_name in ["1974F", "1974O"]:
            return True
    return False


def create_database(excel_file_path: str,
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

    xls = pd.ExcelFile(excel_file_path)

    with sqlite3.connect(database_name) as conn:
        for sheet_name in tqdm(xls.sheet_names):
            if not valid_sheet(sheet_name):
                continue

            try:
                df = pd.read_excel(xls, sheet_name)
                df = clean_and_transform_dataframe(df)
                df.to_sql(sheet_name, conn, index=False, if_exists="replace")
            except Exception as e:
                print(f"Error processing sheet {sheet_name}: {e}")


def main():
    excel_file_path = "1918-2019election_results_by_pcon.xlsx"
    database_name = "elections.db"

    try:
        create_database(excel_file_path, database_name)
        print(f"Database \"{database_name}\" successfully created.")
    except Exception as e:
        print(f"Error creating database: {e}")


if __name__ == "__main__":
    main()
