import pandas as pd

class DataCleaner:

    COUNTRY_CONTINENT_MAP = {
        "BRA": "AMERICA", "JAM": "AMERICA", "MEX": "AMERICA",
        "RD": "AMERICA", "USA": "AMERICA",
        "ESP": "EUROPA", "ITA": "EUROPA"
    }

    NEW_HOTELS_DATA = [
        ("HOTEL ALHAMBRA", "ESP", "3*", "EUROPA"),
        ("HOTEL JUPITER", "ESP", "3*", "EUROPA"),
        ("HOTEL MIRADOR", "ESP", "3*", "EUROPA"),
        ("HOTEL ORION", "ESP", "3*", "EUROPA"),
        ("HOTEL PRISMA", "ESP", "3*", "EUROPA"),
        ("HOTEL QUASAR", "ESP", "3*", "EUROPA"),
        ("HOTEL BOREALIS", "ESP", "5*", "EUROPA"),
        ("HOTEL IRIS", "ESP", "3*", "EUROPA")]
    
    CATEGORY_UPDATE = ["HOTEL BOREALIS", "HOTEL IRIS"]

    HOTEL_EXCLUDED =["HOTEL YARIS"]

    @classmethod
    def _normalize(cls, pnl: pd.DataFrame, hotels: pd.DataFrame):
        pnl =  pnl.copy()
        hotels = hotels.copy()

        #Normalize key column
        pnl["HOTEL"] = pnl["HOTEL"].str.strip().str.title()
        hotels["HOTEL"] = hotels["HOTEL"].str.strip().str.title()

        if "PAIS" in hotels.columns:
            hotels["PAIS"] = hotels["PAIS"].str.strip().str.upper()
        
        if "CONTINENTE" in hotels.columns:
            hotels["CONTINENTE"] = hotels["CONTINENTE"].str.strip().str.upper()
        
        if "CATEGORIA" in hotels.columns:
            hotels["CATEGORIA"] = hotels["CATEGORIA"].str.strip().str.upper()

        return pnl, hotels
    
    #------------------------------------------
    #Enrich hotel data with new entries and fix inconsistencies
    #------------------------------------------
    @classmethod
    def _enrich_hotels(cls, hotels: pd.DataFrame):
        hotels = hotels.copy()
        df_master = pd.DataFrame(cls.NEW_HOTELS_DATA, columns=["HOTEL", "PAIS", "CATEGORIA", "CONTINENTE"])

        df_master["HOTEL"] = df_master["HOTEL"].str.strip().str.upper()
        existing_hotels = set(hotels["HOTEL"])

        #Add new
        new_hotels = df_master[~df_master["HOTEL"].isin(existing_hotels)]
        hotels = pd.concat([hotels, new_hotels], ignore_index=True)

        stars_map = df_master.set_index("HOTEL")["CATEGORIA"].to_dict()
        hotels["CATEGORIA"]= hotels.apply(
            lambda row: stars_map[row["HOTEL"]] 
            if row["HOTEL"] in cls.CATEGORY_UPDATE
            else row["CATEGORIA"], 
            axis=1)
        return hotels
    
    @classmethod
    def _clean_hotels(cls, hotels: pd.DataFrame):

        #------------------------------------------
        #Fix inconsistencies in country names
        #------------------------------------------
        hotels.loc[:,"CONTINENTE"] = hotels["PAIS"].map(cls.COUNTRY_CONTINENT_MAP)
        hotels.loc[:,"CONTINENTE"] = hotels["CONTINENTE"].fillna("UNKNOWN")

        #------------------------------------------
        #Clean categories by removing spaces and asterisks
        #------------------------------------------
        hotels.loc[:,"CATEGORIA"] = ( hotels["CATEGORIA"]
                               .str.replace(" ", "", regex=False)
                               .str.replace("*", "", regex=False))
        hotels = hotels.drop_duplicates(subset=["HOTEL"])

        hotels.loc[:,"PAIS"] = hotels["PAIS"].fillna("UNKNOWN")
        hotels.loc[:,"CATEGORIA"] = hotels["CATEGORIA"].fillna("N/A")

        #Remove duplicates based on HOTEL column, keeping the first occurrence
        hotels = hotels.drop_duplicates(subset=["HOTEL"], keep="first")
        return  hotels
    
   
    #------------------------------------------
    #Get operatitive status (active/close/inactive) for each hotel and period
    #------------------------------------------

    @classmethod
    def _get_operational_status(cls, pnl: pd.DataFrame):
        pnl = pnl.copy()
        pnl["DATE_VAL"] = pnl["ANIO"] * 100 + pnl["MES"]

        pnl["IS_OPEN"] = (
            (pnl["ESCENARIO"] == "BUDGET") |
            ((pnl["ESCENARIO"] == "REAL") &
             ((pnl["RN"] > 0) | (pnl["OPERATING_REVENUE"] != 0)))
        )

        monthly = (
            pnl.groupby(["HOTEL", "ANIO", "MES", "DATE_VAL"])["IS_OPEN"]
            .max()
            .reset_index()
        )

        monthly["MES_STR"] = (
            monthly["ANIO"].astype(str) + "-" +
            monthly["MES"].astype(str).str.zfill(2)
        )

        summary = []
        max_period = monthly["DATE_VAL"].max()

        for hotel, group in monthly.groupby("HOTEL"):
            group = group.sort_values("DATE_VAL")

            open_months = group[group["IS_OPEN"]]["MES_STR"].tolist()
            last_open = group[group["IS_OPEN"]]["DATE_VAL"].max()

            status = "ACTIVE"
            period_close = "N/A"

            if pd.isna(last_open):
                status = "INACTIVE"
                period_close = "UNKNOWN"

            elif last_open < max_period:
                status = "CLOSED"
                next_months = group[group["DATE_VAL"] > last_open]
                period_close = (
                    next_months["MES_STR"].iloc[0]
                    if not next_months.empty else "CLOSED"
                )
            summary.append({
                "HOTEL": hotel,
                 "MONTHS_OPEN": ", ".join(open_months) if open_months else "NONE",
                 "STATUS": status,
                "PERIOD_CLOSE": period_close
            })
        return pd.DataFrame(summary)
    #------------------------------------------
    #Pipeline final
    #------------------------------------------

    @classmethod
    def clean(cls, pnl: pd.DataFrame, hotels: pd.DataFrame) -> pd.DataFrame:
        #Normalize
        pnl, hotels = cls._normalize(pnl, hotels)
        #Enrich
        hotels = cls._enrich_hotels(hotels)
        #Clean
        hotels = cls._clean_hotels(hotels)
        #get operational status
        status = cls._get_operational_status(pnl)

        hotels = hotels.merge(status, on="HOTEL", how="left")

        hotels["STATUS"] = hotels["STATUS"].fillna("INACTIVE")
        hotels["PERIOD_CLOSE"] = hotels["PERIOD_CLOSE"].fillna("UNKNOWN")
        hotels["MONTHS_OPEN"] = hotels["MONTHS_OPEN"].fillna("INACTIVE")

        #hotels_tmp = hotels.drop(columns=["PERIOD_CLOSE","MONTHS_OPEN","STATUS"])
        pnl_tmp = pnl[~pnl['HOTEL'].isin(cls.HOTEL_EXCLUDED)]

        df = pnl_tmp.merge(hotels, on="HOTEL", how="left")
        return df
