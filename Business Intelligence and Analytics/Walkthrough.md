# Step 1: Pilih 5 Business Process dan Buat Business Requirements-nya

### Contoh Business Process dari dataset Supply Chain:

#### Fact ORDER
🎯 **Purpose of Creating a Fact Table**  
In a data warehouse, the fact table is the core table that captures the measurable business events.  
In your case, that’s **orders**, so `fact_order` is the central table for analyzing sales transactions.


#### Shipping & Delivery
🎯 **Purpose of This Fact Table**  
This fact table helps answer logistics performance questions, such as:
- How long does shipping take per region?  
- How often are deliveries delayed?  
- Which shipping modes are most efficient?  
- Is a certain market more prone to late deliveries?  

---

#### Customer Management  


---

#### Shipping & Fulfillment  
With Fact_Product_Stats, you can easily:
- Rank products by profitability.
- Calculate conversion ratios (e.g., profit margin over sales).
- Do cohort analysis (e.g., compare product performance for new vs. returning customers).
- Feed clean data into ML models (sales forecasting, product recommendation).

---

#### Fact Sales
🎯 **Purpose of This Fact Table**  
Easy to run KPIs like:
- Total revenue this month  
- Profit by product category  
- Discount trend per market  
without jumping across multiple tables.

---

### Business Requirements (Contoh)

- **Sales & Revenue:**  
  "Manajemen ingin mengetahui produk mana yang menyumbang revenue terbesar per bulan dan per wilayah."  

- **Shipping:**  
  "Tim operasional ingin menganalisis durasi pengiriman rata-rata berdasarkan kota dan jasa pengiriman."  

---

# Step 2: Lakukan Dimension Modelling
Untuk setiap business process, buat:

- **Fact Table** (misalnya: `FactSales`, `FactShipping`)  
- **Dimension Table** yang relevan:  
  - `DimCustomer`  
  - `DimProduct`  
  - `DimLocation`  
  - `DimDate`  
  - `DimShipping`  
  - `DimMarket`

✔️ Gunakan **Star Schema** dan buat **bus matrix** juga 
---

# Step 3: Lakukan Proses ETL dengan Pentaho

### Extract  
- Load CSV ke Pentaho (gunakan input step seperti **Text File Input**).

### Transform  
- Cleaning (format tanggal, hilangkan duplikasi/null)  
- Join ke dimension (pakai **lookup step**)  
- Tambah kolom **surrogate key** jika perlu  

### Load  
- Masukkan ke tabel OLAP (misalnya database **MySQL/PostgreSQL/SQLite**).  

💡 Buat **1 ETL flow untuk setiap business process** (atau gabung semua jika sudah modular).

---

# Step 4: Visualisasi OLAP (BI Dashboard)

Gunakan tools seperti:
- Google Data Studio / Looker  
- Power BI  
- Metabase  
- Tableau Public  

### Contoh visualisasi:
- Revenue trend per bulan  
- Top 10 produk berdasarkan revenue  
- Lama pengiriman per kota  
- Performa produk per market  

➡️ Gunakan hasil query dari OLAP database hasil ETL.
