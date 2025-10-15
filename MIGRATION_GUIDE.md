# Database Migration Guide

## Important: Price Field Change

The Product model's `price` field has been changed from `CharField` to `DecimalField`. This requires careful migration.

## Option 1: Fresh Database (Recommended for Development)

If you don't have important data, the easiest approach:

```bash
cd "FINAL (3)/furnitureshop"

# Delete the database
del db.sqlite3  # Windows
# rm db.sqlite3  # Linux/Mac

# Delete all migration files except __init__.py
# Keep: shop/migrations/__init__.py and accounts/migrations/__init__.py
# Delete: All numbered migration files (0001_initial.py, etc.)

# Create fresh migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## Option 2: Preserve Existing Data

If you have important data to preserve:

### Step 1: Backup Database
```bash
# Make a backup copy
copy db.sqlite3 db.sqlite3.backup  # Windows
# cp db.sqlite3 db.sqlite3.backup  # Linux/Mac
```

### Step 2: Export Product Data
```bash
python manage.py shell
```

```python
from shop.models import Product
import json

# Export products to JSON
products = []
for p in Product.objects.all():
    products.append({
        'name': p.name,
        'category_id': p.category_id,
        'price': str(p.price),  # Convert to string
        'discount': p.discount,
        'rating': str(p.rating),
        'description': p.description,
        'image': p.image.name if p.image else None
    })

with open('products_backup.json', 'w') as f:
    json.dump(products, f, indent=2)

print(f"Exported {len(products)} products")
exit()
```

### Step 3: Create New Migration
```bash
python manage.py makemigrations
```

### Step 4: Apply Migration
```bash
python manage.py migrate
```

### Step 5: Re-import Products
```bash
python manage.py shell
```

```python
from shop.models import Product, Category
from decimal import Decimal
import json

with open('products_backup.json', 'r') as f:
    products = json.load(f)

for p_data in products:
    try:
        Product.objects.create(
            name=p_data['name'],
            category_id=p_data['category_id'],
            price=Decimal(p_data['price']),
            discount=p_data['discount'],
            rating=Decimal(p_data['rating']),
            description=p_data['description'],
            image=p_data['image']
        )
        print(f"Imported: {p_data['name']}")
    except Exception as e:
        print(f"Error importing {p_data['name']}: {e}")

print("Import complete!")
exit()
```

## Option 3: Manual SQL Migration (Advanced)

For SQLite database:

```bash
python manage.py dbshell
```

```sql
-- Create new table with correct schema
CREATE TABLE shop_product_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    discount INTEGER NOT NULL DEFAULT 0,
    rating DECIMAL(3, 2) NOT NULL DEFAULT 0,
    image VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES shop_category(id)
);

-- Copy data with type conversion
INSERT INTO shop_product_new 
SELECT 
    id, 
    name, 
    slug, 
    CAST(price AS DECIMAL), 
    discount, 
    rating, 
    image, 
    description, 
    created_at, 
    category_id 
FROM shop_product;

-- Drop old table
DROP TABLE shop_product;

-- Rename new table
ALTER TABLE shop_product_new RENAME TO shop_product;

.quit
```

## Verification

After migration, verify everything works:

```bash
python manage.py shell
```

```python
from shop.models import Product
from decimal import Decimal

# Check a product
p = Product.objects.first()
print(f"Product: {p.name}")
print(f"Price type: {type(p.price)}")
print(f"Price value: {p.price}")
print(f"Discounted: {p.discounted_price()}")

# Verify it's a Decimal
assert isinstance(p.price, Decimal), "Price should be Decimal!"
print("✅ Price field is correctly a Decimal")
exit()
```

## Troubleshooting

### Error: "No such column: shop_product.price"
- Run `python manage.py migrate --fake-initial` if migrations are out of sync

### Error: "Invalid literal for Decimal"
- Some prices might have invalid characters
- Clean data before migration

### Error: "UNIQUE constraint failed"
- Slugs might be duplicated
- Clear slugs before migration or ensure uniqueness

## After Migration

1. Test all features:
   - Browse products
   - Add to cart
   - Checkout
   - View orders

2. Check admin panel:
   - Products display correctly
   - Prices show with 2 decimal places
   - Discounted prices calculate correctly

3. Monitor logs for any decimal-related errors

---

**Choose the option that best fits your situation. Option 1 is recommended for development environments.**