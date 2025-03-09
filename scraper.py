import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Nastavení WebDriveru
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Otevři stránku s mléčnými výrobky
driver.get("https://www.rohlik.cz/hledat?q=ml%C3%A9%C4%8Dn%C4%9B%20v%C3%BDrobky&companyId=1")
time.sleep(5)

data = []

# Názvy a ceny (celkem)
product_names  = driver.find_elements(By.CSS_SELECTOR, "[data-test='productCard-body-name']")
product_prices = driver.find_elements(By.CSS_SELECTOR, "[data-test='productCard-body-price']")

# Hmotnost a cena/kg (unit price)
product_weights    = driver.find_elements(By.CSS_SELECTOR, "[data-test='productCard-footer-amount']")
product_unitprices = driver.find_elements(By.CSS_SELECTOR, "[data-test='productCard-footer-unitPrice']")

# Odkaz na detail produktu
product_links = driver.find_elements(By.CSS_SELECTOR, "[data-test='productCard-header-image'] a")

# Ověříme, zda je všech pět seznamů stejné délky
if (
    len(product_names)     == len(product_prices)   ==
    len(product_weights)   == len(product_unitprices) ==
    len(product_links)
):
    for name_el, price_el, weight_el, unitprice_el, link_el in zip(
        product_names, product_prices, product_weights, product_unitprices, product_links
    ):
        # ====== 1) Název ======
        name_text = name_el.text.strip()

        # ====== 2) Cena celkem ======
        raw_price = price_el.text.replace("\n", "").replace("\u00a0", "").strip()
        raw_price = raw_price.replace("Kč", "").strip()   # odstranění "Kč"
        # nahradíme bílé znaky tečkou
        price_with_dot = re.sub(r'\s+', '.', raw_price)
        # pokud je 4ciferné číslo, tak předěláme "2790" → "27.90"
        if re.match(r'^\d{4}$', price_with_dot):
            price_with_dot = price_with_dot[:2] + '.' + price_with_dot[2:]
        elif re.match(r'^\d{3}$', price_with_dot):
            price_with_dot = price_with_dot[0] + '.' + price_with_dot[1:]
        try:
            price_float = float(price_with_dot)
            final_price = f"{price_float:.2f}".replace('.', ',') + " Kč"
        except ValueError:
            final_price = "0,00 Kč"

        # ====== 3) Hmotnost ======
        weight_text = weight_el.text.strip()  # např. "125 g"

        # ====== 4) Cena za 1 kg ======
        unit_text = unitprice_el.text.strip() # např. "223,2 Kč/kg"

        # ====== 5) Odkaz na detail ======
        relative_url = link_el.get_attribute("href")

        full_url = relative_url

        data.append([name_text, final_price, weight_text, unit_text, full_url])
else:
    print("⚠️ POZOR! Počet prvků nesedí. Zkontroluj selektory.")

driver.quit()

# Uložíme do CSV
df = pd.DataFrame(data, columns=["Název", "Cena", "Hmotnost", "Cena/kg", "Odkaz"])
df.to_csv("rohlik.csv", index=False, encoding="utf-8")
print("✅ Data byla uložena do 'rohlik_ceny.csv'")
