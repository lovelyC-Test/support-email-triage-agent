# The data set

Everything in `raw/` describes one fictional company. The help articles, the
orders, and the sample emails are written to agree with each other, because the
pipeline can only be demonstrated end to end if an email's correct answer
actually exists in the articles and its order number actually exists in the
orders table.

## The company

**ACE Appliance** — a small UK retailer of kitchen appliances.

### Products

- **K7** kettle, 1.7L rapid boil
- **K7 Pro** kettle, adds temperature control
- **T3** toaster, 2 slice
- **T5** toaster, 4 slice
- **G2** coffee grinder, 12 grind settings
- **B1** blender, 1.5L jug
- **Water filter cartridges**, sold singly or on a 3-monthly subscription
- **Descaler sachets**, boxes of six

### Policies

- Returns within **30 days of delivery**, unused and in original packaging.
- Items damaged, faulty or incomplete on arrival have **no time limit** and free
  return postage.
- Refunds reach the original payment method in **5-7 working days** after a
  return is approved.
- **2-year warranty** on all appliances.
- Delivery £3.95, free over £40, 2-3 working days in the UK.
- Filter subscriptions renew every 3 months and can be cancelled at any time.
- Opened filter cartridges and descaler sachets are **non-returnable** unless
  faulty.

## Deliberately not covered

The articles say nothing about these, so that retrieval genuinely fails and the
gate genuinely escalates. Do not add articles for them.

- Use with third-party inverters, generators, or caravan power supplies
- Commercial or catering use
- Legal advice
- Recipes or food preparation

## Files

- `raw/help_articles/*.md` — what retrieval indexes and the composer cites.
- `raw/orders.csv` — seed for the orders table the `order_lookup` tool reads.
- `raw/emails/*.txt` — sample emails, one per file, headers included.
- `raw/emails/labels.csv` — the hand-labelled subset used to measure classifier
  accuracy. Only these have ground truth.

## Conventions

Emails keep their `From:` and `Subject:` headers, and most carry a signature
block, a quoted reply chain, or a legal disclaimer, because stripping those is
intake's job and it needs realistic input to be tested against.

Order numbers are five digits. Any order number appearing in an email that is
**not** in `orders.csv` is there on purpose, to exercise the `order_not_found`
path.
