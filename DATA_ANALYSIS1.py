import streamlit as st
import polars as pl
st.set_page_config(layout="wide")
col1 , col2, col3, col4 = st.columns(4)
with st.sidebar:
    file = st.file_uploader("upload file here")
try:
    copy2 = pl.read_csv(
        file,
        has_header=True,
        schema_overrides={"arrival_data": pl.Date})
    copy2 = pl.DataFrame(copy2)
    total_revenue = sum(copy2["adr"])
    total_bookings= len(copy2)
    total_canceled = sum(copy2["is_canceled"])
    total_customers= copy2["name"].n_unique()

    start = col4.date_input("start date:", min_value=copy2["arrival_data"].min(), max_value=copy2["arrival_data"].max(),
                            value=copy2["arrival_data"].min())
    end = col4.date_input("end date:", min_value=copy2["arrival_data"].min(), max_value=copy2["arrival_data"].max(),
                            value=copy2["arrival_data"].max())
    if start>=end:
        col4.warning("'start' date is greater than or equal 'end' date!")
    else:
        copy2 = copy2.filter((copy2["arrival_data"]>=start) & (copy2["arrival_data"]<=end))
    col4.text("             --------------------      ")
    select = col4.selectbox("filter by:", ["customers", "agents", "companies"], width=150)
    if select =="customers":
        customers = col4.multiselect("Customers:",sorted([co for co in copy2["name"].unique() if co!=0]),width=225)
        if len(customers) > 0:
            copy2 = copy2.filter(copy2["name"].is_in(customers))
            agents = col4.multiselect("Agents:", sorted([co for co in copy2["agent"].unique() if co != 0]), width=225)
            if len(agents)>0:
                copy2 = copy2.filter(copy2["agent"].is_in(agents))
            companies = col4.multiselect("Companies:",sorted([co for co in copy2["company"].unique() if co != 0]),
                                         width=225)
            if len(companies)>0:
                copy2 = copy2.filter(copy2["company"].is_in(companies))
    elif select == "agents":
        agents=col4.multiselect("Agents:",sorted([co for co in copy2["agent"].unique() if co!=0]),width=225)
        if len(agents)>0:
            copy2 = copy2.filter(copy2["agent"].is_in(agents))
            customers = col4.multiselect("Customers:", sorted([co for co in copy2["name"].unique() if co != 0]),
                                         width=225)
            if len(customers)>0:
                copy2 = copy2.filter(copy2["name"].is_in(customers))
    elif select == "companies":
        companies=col4.multiselect("Companies:",sorted([co for co in copy2["company"].unique() if co!=0]),
                                   width=225)
        if len(companies)>0:
            copy2 = copy2.filter(copy2["company"].is_in(companies))
            customers = col4.multiselect("Customers:", sorted([co for co in copy2["name"].unique() if co != 0]),
                                         width=225)
            if len(customers)>0:
                copy2 = copy2.filter(copy2["name"].is_in(customers))
    col4.text("-------  -------  -------  -------")
    col4.markdown("\n\n\n\nabdalhaym09@gmail.com")

    display_total = col2.pills(options=["Rev", "Book", "Cancel", "Custm"], label="Display Total:")
    if display_total =="Rev":
        col2.text(f"{sum(copy2["adr"])}{" " * 10} {(sum(copy2["adr"])*100)/total_revenue:.2f}% of total revenue")
    if display_total =="Book":
        col2.text(f"{copy2["adr"].count()}{" " * 10}{(copy2["adr"].count()*100)/total_bookings:.2f}% of total bookings")
    if display_total =="Cancel":
        col2.text(f"{sum(copy2["is_canceled"])}{" " * 10}{(sum(copy2["is_canceled"])*100)/total_canceled:.2f}%"
                  f" of total cancellations")
    if display_total =="Custm":
        col2.text(f"{copy2["name"].n_unique()} {" " * 10} {(copy2["name"].n_unique()*100) / total_customers:.2f}% of total"
                  f"customers")
    col2.text("    -----------------------------------------------       ")
    subject = col1.selectbox("subject:", ["Revenue","Bookings","Cancellation"])
    time_line = (copy2.group_by("arrival_data").agg([pl.sum("adr").alias("Revenue"),
                                                     pl.count("adr").alias("Bookings"),
                                                     pl.sum("is_canceled").alias("Cancellation")]
                                                     ).sort("arrival_data", descending=True))
    col1.line_chart(data=time_line, x="arrival_data", y=subject, width = 300, height= 250)
    col1.text("      ------------------------------------------------  ")
    rooms = (copy2.group_by("reserved_room_type").agg([pl.sum("adr").alias("Revenue"),
                                                       pl.count("adr").alias("Bookings"),
                                                       pl.sum("is_canceled").alias("Cancellation")]
                                                      ).sort("reserved_room_type", descending=True))
    col2.bar_chart(data=rooms, x="reserved_room_type", y=subject, width = 300, height= 150)

    customer_types = (copy2.group_by("customer_type").agg([pl.sum("adr").alias("Revenue"),
                                                       pl.count("adr").alias("Bookings"),
                                                       pl.sum("is_canceled").alias("Cancellation")]
                                                      ).sort(subject, descending=False))
    col1.bar_chart(data=customer_types, x="customer_type", y=subject, width = 300, height= 230, horizontal=True)

    copy2 = copy2.map_columns("agent", lambda x:x.replace(0, None))
    copy2 = copy2.map_columns("company", lambda x:x.replace(0, None))
    by = col3.selectbox("Top 15", ["Customers", "Agents", "Companies"])
    if by=="Customers":
        by = "name"
    elif by=="Agents":
        by = "agent"
    else:
        by = "company"
    top = (copy2.group_by(by).agg([pl.sum("adr").alias("Revenue"),
                                                       pl.count("adr").alias("Bookings"),
                                                       pl.sum("is_canceled").alias("Cancellation")]
                                                      ).sort(subject, descending=True)).head(16)
    top = top.drop_nulls()
    col3.bar_chart(data=top, x=by, y=subject, width = 300, height= 300)

    copy2 = copy2.filter(copy2["lead_time"]<300)
    lead_time = (copy2.group_by("lead_time").agg([pl.sum("adr").alias("Revenue"),
                                                     pl.count("adr").alias("Bookings"),
                                                     pl.sum("is_canceled").alias("Cancellation")]
                                                     ).sort("lead_time", descending=True))
    col3.area_chart(data=lead_time, x="lead_time", y=subject, width = 300, height= 250, color="#84e0f5")

    means=(copy2.group_by("arrival_data").agg([pl.mean("adr").alias("mean adr")]).sort("arrival_data",
                                                                                       descending=True))
    col2.scatter_chart(data=means, x="arrival_data", y="mean adr", width = 300, height= 180, color="#84e0f5")

    deposit = (copy2.group_by("deposit_type").agg([pl.sum("adr").alias("Revenue"),
                                                       pl.count("adr").alias("Bookings"),
                                                       pl.sum("is_canceled").alias("Cancellation")]
                                                      ).sort(subject, descending=False))
    col2.bar_chart(data=deposit, x="deposit_type", y=subject, width = 300, height= 200, horizontal=True)
except TypeError:
    st.warning("←pleas upload file in the sidebar")
except pl.exceptions.ComputeError:
    st.warning("somthing went wrong!\npleas make sure its the right file")