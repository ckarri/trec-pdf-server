#!/usr/bin/env python3
"""
TREC PDF Generator — Railway Production Server
Fills TREC 20-18, 40-11, 36-10 and returns merged PDF

Environment variables (set in Railway dashboard):
  BROKERAGE_PASSWORD  — password agents use to access the tool
  PORT                — automatically set by Railway
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, io, sys
from pypdf import PdfReader, PdfWriter
from datetime import datetime, timedelta

BASE     = os.path.dirname(os.path.abspath(__file__))
PDF_14   = os.path.join(BASE, 'trec_20_18.pdf')
PDF_FIN  = os.path.join(BASE, '40-11.pdf')
PDF_HOA  = os.path.join(BASE, '36-10.pdf')
PORT     = int(os.environ.get('PORT', 8765))
PASSWORD = os.environ.get('BROKERAGE_PASSWORD', 'Ramchandra2025!')

# ── DEFAULTS ──────────────────────────────────────────────────────────────────
DEFAULTS = {
    'buyer_type':'Individual','state':'TX',
    'close_days':'30','earnest_deposit_days':'3',
    'option_days':'7','option_fee':'$100',
    'title_policy_paid_by':'Seller',
    'survey_days':'7','title_objection_days':'5',
    'as_is':True,'repairs':'As-Is','hoa':'no',
    'earnest_form':'Check','option_fee_form':'Check',
    'buyer_approval_days':'21','loan_term_years':'30',
    'max_interest_rate':'10','origination_charges_pct':'3',
    'hoa_subdivision_days':'7','hoa_transfer_fee_cap':'500',
}

def apply_defaults(data):
    d = dict(data)
    for k, val in DEFAULTS.items():
        if not d.get(k): d[k] = val
    today = datetime.today()
    MONTHS = ["January","February","March","April","May","June","July",
              "August","September","October","November","December"]
    cd = today + timedelta(days=int(d.get('close_days', 30)))
    d['close_month_day'] = MONTHS[cd.month-1] + ' ' + str(cd.day)
    d['close_year'] = str(cd.year)
    if not d.get('close_date'):
        d['close_date'] = d['close_month_day'] + ', ' + d['close_year']
    od = today + timedelta(days=int(d.get('option_days', 7)))
    if not d.get('option_expiry'):
        d['option_expiry'] = MONTHS[od.month-1] + ' ' + str(od.day) + ', ' + str(od.year)
    if d.get('sales_price') and not d.get('cash_portion'):
        try:
            price = float(str(d['sales_price']).replace('$','').replace(',',''))
            pct   = float(str(d.get('down_payment_pct','20')).replace('%','')) / 100
            d['cash_portion'] = '${:,.0f}'.format(price * pct)
            d['loan_amount']  = '${:,.0f}'.format(price * (1 - pct))
        except: pass
    if 'cash' in str(d.get('loan_type','')).lower():
        d['financing_addendum'] = False
        d['cash_portion'] = d.get('sales_price','')
        d['loan_amount']  = ''
    if d.get('hoa','').lower() == 'yes': d['hoa_addendum'] = True
    try:
        if int(d.get('year_built', 9999)) < 1978: d['lead_paint_addendum'] = True
    except: pass
    d['prop_header'] = ' '.join(filter(None,[
        d.get('property_address',''), d.get('city',''),
        'TX' if d.get('city') else '', d.get('zip','')
    ]))
    return d

def v(d, k, dflt=''):
    val = d.get(k)
    return str(val).strip() if val else dflt

def fill_main(d):
    prop = v(d,'prop_header')
    reader = PdfReader(PDF_14)
    writer = PdfWriter()
    writer.clone_reader_document_root(reader)
    writer.update_page_form_field_values(None, {
        '1 PARTIES The parties to this contract are': v(d,'seller_name'),
        'Seller and': v(d,'buyer_name'),
        'A LAND Lot': v(d,'lot'), 'Block': v(d,'block'), 'undefined': v(d,'subdivision'),
        'Addition City of': v(d,'city'), 'County of': v(d,'county'),
        'Texas known as': v(d,'property_address') + ', ' + v(d,'zip'),
        'undefined_2': v(d,'cash_portion'), 'undefined_3': v(d,'loan_amount'),
        'undefined_4': v(d,'sales_price'), 'undefined_5': v(d,'sales_price'),
        'Contract Concerning': prop, 'Contract Concerning_2': prop,
        'Contract Concerning_3': prop, 'Contract Concerning_4': prop,
        'Address of Property': prop, 'Address of Property_2': prop, 'Addr of Prop': prop,
        'insurance Title Policy issued by': v(d,'title_company'),
        'as earnest money to': v(d,'title_company'),
        'as earnest money to 2': v(d,'title_company_address'),
        'the Title Company and Buyers lenders Check one box only': v(d,'survey_days','7'),
        'than 3 days prior to Closing Date': v(d,'survey_days','7'),
        'the Commitment Exception Documents and the survey Buyers failure to object within the': v(d,'title_objection_days','5'),
        'A The closing of the sale will be on or before': v(d,'close_month_day'), '20': v(d,'close_year'),
        'Brokers and Sales': v(d,'buyer_agent_name'), 'Brokers and Sales 2': v(d,'buyer_agent_license'),
        'service contract in an amount not exceeding': v(d,'home_warranty_amt'),
        'Text3': v(d,'earnest_money_amt'), 'Text3 2': v(d,'option_fee'), 'Text3 3': v(d,'option_days'),
        'to escrow agent within': v(d,'earnest_deposit_days','3'),
        'to escrow agent within 1': v(d,'title_company'),
        'acknowledged by Seller and Buyers agreement to pay Seller2': v(d,'option_days'),
        'acknowledged by Seller and Buyers agreement to pay Seller 1': v(d,'option_fee'),
        'acknowledged by Seller and Buyers agreement to pay Seller': v(d,'earnest_money_amt'),
        'AC numb 1': v(d,'special_provisions'),
        'when mailed to handdelivered at or transmitted by fax or electronic transmission as follows': v(d,'buyer_address'),
        'at': v(d,'buyer_phone'), 'AC4': v(d,'buyer_email'),
        'undefined_19': v(d,'seller_address'), 'at_2': v(d,'seller_phone'), 'Phone 52': v(d,'seller_email'),
        'Phone11': v(d,'buyer_agent_phone'), 'Phone 2': v(d,'listing_agent_phone'),
        'Text6': v(d,'buyer_agent_email'), 'Text7': v(d,'listing_agent_email'),
        'Listing Broker Firm': v(d,'listing_broker_firm'), 'License No_4': v(d,'listing_broker_license'),
        'List Assoc Name': v(d,'listing_agent_name'), 'License No_5': v(d,'listing_agent_license'),
        'Listing Associates Email Address': v(d,'listing_agent_email'), 'Phone_3': v(d,'listing_agent_phone'),
        'Listing Brokers Office Address': v(d,'listing_broker_address'),
        'City_2': v(d,'listing_broker_city'), 'State_2': 'TX', 'Zip_2': v(d,'listing_broker_zip'),
        'Other Broker Firm': v(d,'buyer_broker_firm'), 'License No': v(d,'buyer_broker_license'),
        'Associates Name numb 1': v(d,'buyer_agent_name'), 'License No_2': v(d,'buyer_agent_license'),
        'Associates Email Address': v(d,'buyer_agent_email'), 'Phone': v(d,'buyer_agent_phone'),
        'Other Brokers Address': v(d,'buyer_broker_address'),
        'City': v(d,'buyer_broker_city'), 'State': 'TX', 'Zip': v(d,'buyer_broker_zip'),
        'Selling Associates Name': v(d,'buyer_agent_name'),
        'Selling Associates Name-1': v(d,'buyer_agent_name'),
        'Selling Associates Email Address': v(d,'buyer_agent_email'), 'Phone_5': v(d,'buyer_agent_phone'),
        'Selling Associates Office Address': v(d,'buyer_broker_address'),
        'City_3': v(d,'buyer_broker_city'), 'State_3': 'TX', 'Zip_3': v(d,'buyer_broker_zip'),
        'Earnest Money in the form of': v(d,'earnest_form','Check'),
        'Option Fee in the form of': v(d,'option_fee_form','Check'),
        'Escrow Agent': v(d,'title_company'), 'Escrow Agent_2': v(d,'title_company'), 'Escrow Agent_3': v(d,'title_company'),
        'Address': v(d,'title_company_address'), 'Address_2': v(d,'title_company_address'), 'Address_3': v(d,'title_company_address'),
        'State_4': 'TX', 'State_5': 'TX', 'State_6': 'TX',
    })
    loan = v(d,'loan_type','').lower()
    cb = {}
    if d.get('financing_addendum', True) and 'cash' not in loan:
        cb['Third Party Financing Addendum'] = '/On'
        cb['B Sum of all financing described in the attached'] = '/On'
    cb['A TITLE POLICY Seller shall furnish to Buyer at'] = '/On' if 'seller' in v(d,'title_policy_paid_by','Seller').lower() else None
    if cb.get('A TITLE POLICY Seller shall furnish to Buyer at') is None:
        cb['Sellers'] = '/On'
        del cb['A TITLE POLICY Seller shall furnish to Buyer at']
    else:
        pass
    cb['1Within'] = '/On'
    cb['i will not be amended or deleted from the title policy or'] = '/On'
    cb['2 Within'] = '/On'
    if d.get('as_is', True):
        cb['As Is'] = '/On'; cb['1 Buyer accepts the Property As Is'] = '/On'
    else:
        cb['As Is except'] = '/On'
        cb['2 Buyer accepts the Property As Is provided Seller at Sellers expense shall complete the'] = '/On'
    cb['upon'] = '/On'
    if v(d,'hoa','no').lower() == 'yes':
        cb['is'] = '/On'; cb['Addendum for Property Subject to'] = '/On'
    else:
        cb['is not'] = '/On'
    cb['Buyer only'] = '/On'
    if d.get('lead_paint_addendum'): cb['Addend. for Sellers Disclos'] = '/On'
    writer.update_page_form_field_values(None, cb)
    buf = io.BytesIO(); writer.write(buf); return buf.getvalue()

def fill_financing(d):
    if not os.path.exists(PDF_FIN): return None
    prop = v(d,'prop_header')
    loan = v(d,'loan_type','').lower()
    term = v(d,'loan_term_years','30')
    max_rate = v(d,'max_interest_rate','10')
    orig_pct = v(d,'origination_charges_pct','3')
    appr_days = v(d,'buyer_approval_days','21')
    reader = PdfReader(PDF_FIN); writer = PdfWriter(); writer.clone_reader_document_root(reader)
    txt = {'Street Address and City': prop, 'Address of Property': prop}
    if 'conventional' in loan:
        try:
            loan_num = float(str(d.get('loan_amount','')).replace('$','').replace(',',''))
            txt['any financed PMI premium due in full in 1'] = '${:,.0f}'.format(loan_num)
        except: txt['any financed PMI premium due in full in 1'] = v(d,'loan_amount')
        txt['any financed PMI premium due in full in 2'] = term
        txt['per annum for the first'] = '1'
        txt['shown on Buyers Loan Estimate for the loan not to exceed'] = orig_pct
        txt['years with interest not to exceed'] = max_rate
    elif 'fha' in loan:
        txt['undefined'] = '203(b)'
        txt['excluding any financed MIP amortizable monthly for not less'] = v(d,'loan_amount')
        txt['than'] = term
        txt['years with interest not to exceed_2'] = max_rate
        txt['Charges as shown on Buyers Loan Estimate for the loan not to exceed'] = orig_pct
    elif 'va' in loan:
        txt['excluding any financed Funding Fee amortizable monthly for not less than'] = v(d,'loan_amount')
        txt['years'] = term
        txt['with interest not to exceed'] = max_rate
        txt['per annum for the first_4'] = '1'
        txt['Origination Charges as shown on Buyers Loan Estimate for the loan not to exceed'] = orig_pct
    elif 'usda' in loan:
        txt['any financed Funding Fee amortizable monthly for not less than'] = v(d,'loan_amount')
        txt['not to exceed_2'] = term
        txt['per annum for the first_3'] = max_rate
        txt['not to exceed'] = orig_pct
    txt['value of the Property established by the Department of Veterans Affairs'] = appr_days
    if 'fha' in loan or 'va' in loan: txt['Text1'] = v(d,'sales_price')
    writer.update_page_form_field_values(None, txt)
    cb = {}
    if 'conventional' in loan:
        cb['1 Conventional Financing'] = '/On'
        cb['a A first mortgage loan in the principal amount of'] = '/On'
    elif 'fha' in loan: cb['3 FHA Insured Financing A Section'] = '/On'
    elif 'va' in loan: cb['4 VA Guaranteed Financing A VA guaranteed loan of not less than'] = '/On'
    elif 'usda' in loan: cb['5 USDA Guaranteed Financing A USDAguaranteed loan of not less than'] = '/On'
    cb['This contract is subject to Buyer obtaining Buyer Approval If Buyer cannot obtain Buyer'] = '/On'
    writer.update_page_form_field_values(None, cb)
    buf = io.BytesIO(); writer.write(buf); return buf.getvalue()

def fill_hoa(d):
    if not os.path.exists(PDF_HOA): return None
    prop = v(d,'prop_header')
    reader = PdfReader(PDF_HOA); writer = PdfWriter(); writer.clone_reader_document_root(reader)
    writer.update_page_form_field_values(None, {
        'Street Address and City': prop,
        'Name of Property Owners Association Association and Phone Number': v(d,'hoa_name'),
        'the Subdivision Information to the Buyer If Seller delivers the Subdivision Information Buyer may terminate': v(d,'hoa_subdivision_days','7'),
        'D DEPOSITS FOR RESERVES Buyer shall pay any deposits for reserves required at closing by the Association': '$' + v(d,'hoa_transfer_fee_cap','500'),
    })
    writer.update_page_form_field_values(None, {
        '1 Within': '/On',
        'Seller shall pay the Title Company the cost of obtaining the': '/On',
    })
    buf = io.BytesIO(); writer.write(buf); return buf.getvalue()

def merge_pdfs(pdf_list):
    writer = PdfWriter()
    for pdf in pdf_list:
        if pdf:
            for page in PdfReader(io.BytesIO(pdf)).pages:
                writer.add_page(page)
    buf = io.BytesIO(); writer.write(buf); return buf.getvalue()

def generate_all(raw_data):
    d = apply_defaults(raw_data)
    loan = str(d.get('loan_type','')).lower()
    pdfs = []; names = []
    pdfs.append(fill_main(d)); names.append('TREC 20-18')
    if 'cash' not in loan and d.get('financing_addendum', True):
        f = fill_financing(d)
        if f: pdfs.append(f); names.append('TREC 40-11')
    if str(d.get('hoa','no')).lower() == 'yes':
        h = fill_hoa(d)
        if h: pdfs.append(h); names.append('TREC 36-10')
    return merge_pdfs(pdfs), names


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a): pass

    def cors(self):
        # Allow requests from any Netlify domain or localhost
        origin = self.headers.get('Origin', '')
        self.send_header('Access-Control-Allow-Origin', origin or '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Password')
        self.send_header('Access-Control-Allow-Credentials', 'true')

    def do_OPTIONS(self):
        self.send_response(200); self.cors(); self.end_headers()

    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.cors(); self.end_headers()
            self.wfile.write(json.dumps({'status':'ok','forms':['20-18','40-11','36-10']}).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')

    def do_POST(self):
        # Check password header
        pwd = self.headers.get('X-Password', '')
        if pwd != PASSWORD:
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.cors(); self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid password'}).encode())
            return

        if self.path == '/fill-pdf':
            length = int(self.headers.get('Content-Length', 0))
            body   = self.rfile.read(length)
            try:
                data = json.loads(body)
                addr = data.get('property_address', 'unknown')
                print(f"Generating forms for: {addr}")
                pdf_bytes, form_names = generate_all(data)
                fname = 'TREC_' + (addr or 'Offer').replace(' ','_')[:25] + '.pdf'
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', f'attachment; filename="{fname}"')
                self.send_header('Content-Length', str(len(pdf_bytes)))
                self.send_header('X-Forms-Included', ', '.join(form_names))
                self.cors(); self.end_headers()
                self.wfile.write(pdf_bytes)
                print(f"Done: {', '.join(form_names)} — {len(pdf_bytes):,} bytes")
            except Exception as e:
                import traceback; traceback.print_exc()
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.cors(); self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())


if __name__ == '__main__':
    print(f"\n{'='*50}")
    print(f"  TREC PDF Server — Production (Railway)")
    print(f"{'='*50}")
    for label, path in [('20-18', PDF_14), ('40-11', PDF_FIN), ('36-10', PDF_HOA)]:
        status = '✓' if os.path.exists(path) else '✗ MISSING'
        print(f"  {status}  TREC {label}")
    print(f"  Port: {PORT}")
    print(f"  Password: {'set via env' if os.environ.get('BROKERAGE_PASSWORD') else 'using default'}")
    print(f"{'='*50}\n")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
