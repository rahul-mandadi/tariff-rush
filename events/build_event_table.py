#!/usr/bin/env python3
"""Build a conservative tariff-action table from the local FR cache only.

Run normally to use all currently cached texts. --cached-documents accepts a
comma-separated snapshot of document numbers for reproducibility during harvest.
Exclusions are classified as EXCLUSION and routed to the rejected table.
Quoted schedules can contain historical rates; unresolved main rates stay blank.
"""
import argparse
import csv
import html
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = 'document_number title doc_type agency authority action_kind announcement_date effective_date rate_pct is_increase partners hts_codes hs_chapters url confidence notes'.split()
MONTH = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
DATE = rf'{MONTH}\s+\d{{1,2}},?\s+\d{{4}}'
COUNTRIES = {
    'Canada': r'Canada', 'Mexico': r'Mexico', 'Australia': r'Australia',
    'Argentina': r'Argentina', 'Brazil': r'Brazil', 'South Korea': r'South Korea|Republic of Korea',
    'China': r"China|People.s Republic of China", 'Turkey': r'Turkey|Türkiye',
    'Japan': r'Japan', 'United Kingdom': r'United Kingdom|UK',
    'European Union': r'European Union|EU', 'United Arab Emirates': r'United Arab Emirates',
    'India': r'India', 'Russia': r'Russia|Russian Federation', 'France': r'France',
    'Germany': r'Germany', 'Italy': r'Italy', 'Spain': r'Spain',
    'Vietnam': r'Vietnam|Viet Nam', 'Taiwan': r'Taiwan', 'Switzerland': r'Switzerland',
    'Norway': r'Norway', 'Indonesia': r'Indonesia', 'Malaysia': r'Malaysia',
    'Thailand': r'Thailand', 'South Africa': r'South Africa', 'New Zealand': r'New Zealand',
    'Ukraine': r'Ukraine', 'Chile': r'Chile', 'Singapore': r'Singapore',
    'Israel': r'Israel', 'Colombia': r'Colombia', 'Peru': r'Peru', 'Pakistan': r'Pakistan',
    'Bangladesh': r'Bangladesh', 'Saudi Arabia': r'Saudi Arabia', 'Ireland': r'Ireland',
    'Belgium': r'Belgium', 'Netherlands': r'Netherlands', 'Austria': r'Austria',
    'Sweden': r'Sweden', 'Finland': r'Finland', 'Denmark': r'Denmark', 'Poland': r'Poland',
    'Portugal': r'Portugal', 'Greece': r'Greece', 'Czech Republic': r'Czech Republic|Czechia',
    'Hungary': r'Hungary', 'Romania': r'Romania', 'Bulgaria': r'Bulgaria',
    'Croatia': r'Croatia', 'Cyprus': r'Cyprus', 'Estonia': r'Estonia', 'Latvia': r'Latvia',
    'Lithuania': r'Lithuania', 'Luxembourg': r'Luxembourg', 'Malta': r'Malta',
    'Slovakia': r'Slovakia', 'Slovenia': r'Slovenia',
}


def clean(raw):
    raw = re.sub(r'<[^>]*>', ' ', raw)
    raw = html.unescape(raw).replace('\x00', ' ').replace('\u2014', '-')
    raw = re.sub(r'\[\[Page[^]]*\]\]', ' ', raw)
    return re.sub(r'\s+', ' ', raw).strip()


def authority(text):
    summary = re.search(r'SUMMARY:(.*?)DATES:', text, re.I)
    if summary:
        main = re.search(r'section\s+(232|301|201)\b', summary.group(1), re.I)
        if main:
            return 'SECTION_' + main.group(1), 'Authority identified from current-action summary'
    delegation = re.search(r'By the authority vested in me.{0,1500}?I,', text, re.I)
    if delegation and re.search(r'International Emergency Economic Powers Act|IEEPA', delegation.group(), re.I):
        return 'IEEPA', 'Authority identified from executive order delegation'

    patterns = [
        ('SECTION_232', r'section\s+232\b|19\s+U\.?S\.?C\.?\s+1862'),
        ('SECTION_301', r'section\s+301\s+(?:of\s+the\s+Trade Act|investigation|action)|19\s+U\.?S\.?C\.?\s+2411'),
        ('IEEPA', r'International Emergency Economic Powers Act|\bIEEPA\b'),
        ('SECTION_201', r'section\s+201\s+of\s+the\s+Trade Act|19\s+U\.?S\.?C\.?\s+2251'),
    ]
    found = [name for name, pattern in patterns if re.search(pattern, text, re.I)]
    if len(found) == 1:
        return found[0], ''
    if len(found) > 1:
        return 'UNKNOWN', 'Multiple authorities cited: ' + '; '.join(found)
    if re.search(r'Trading with the Enemy Act|section\s+338\s+of\s+the\s+Tariff Act', text, re.I):
        return 'OTHER', ''
    return 'UNKNOWN', 'No unambiguous tariff authority extracted'


def operative(text):
    # Presidential preambles describe prior actions, not the current decision.
    marker = re.search(r'(?:do hereby proclaim|hereby proclaim|hereby order)\s+as follows:', text, re.I)
    if marker:
        return text[marker.end():]
    marker = re.search(r'do hereby proclaim that', text, re.I)
    if marker:
        return text[marker.end():]
    marker = re.search(r'NOW, THEREFORE', text, re.I)
    return text[marker.start():] if marker else text


def classify(record, text, body):
    title = record['title'].lower()
    if record['type'] == 'Proposed Rule':
        return '', 'PROPOSED_RULE'
    if re.search(r'antidumping|countervailing|less than fair value|circumvention|sunset review', title):
        return '', 'TRADE_REMEDY_CASE'
    if re.search(r'product exclusion|exclusion extensions?|reinstatement of.*exclusions|conforming amendment.*exclusion|exclusion of particular products', title):
        return 'EXCLUSION', 'EXCLUSION'
    if re.search(r'exclusion.*(?:process|portal|request)|submissions.*exclusion|procedures.*(?:relief|exclusion)', title):
        return '', 'EXCLUSION_PROCEDURE'
    if re.search(r'request.*comment|notice of inquiry|publication of a report|information collection|regulatory agenda|semiannual|investigation.*(?:initiation|institution)', title):
        return '', 'ADMINISTRATIVE_OR_INQUIRY'
    if re.search(r'foreign.trade zone|combined notice|electric|gas pipelines|royalty|application fees', title):
        return '', 'UNRELATED_RULEMAKING'
    if re.search(r'import monitoring|domestic interested party petition|technical amendments|suspension of liquidation', title):
        return '', 'ADMINISTRATIVE_OR_TRADE_REMEDY'
    presidential = record['type'] == 'Presidential Document' and re.search(r'imports|tariff|duties|safeguard', title)
    final_notice = re.search(r'(?:notice of (?:modification|determination|action)|implementation of duties|additional duties|tariff rates)', title) and re.search(r'import|goods|HTSUS|consumption', body, re.I)
    if not (presidential or final_notice):
        return '', 'NO_CLEAR_OPERATIVE_TARIFF_ACTION'
    if re.search(r'^.{0,1500}(?:quantitative limitation|relief from the quantitative)', body, re.I) and not re.search(r'^.{0,1500}(?:shall be subject to|shall be exempt|tariff.rate quota)', body, re.I):
        return '', 'QUOTA_OR_RELIEF_ONLY'
    if re.search(r'Proclamation \d+, including the Annex, is revoked', body, re.I):
        return 'REVOKE', ''
    decision = re.search(r'I have determined that.{0,700}', text, re.I)
    if decision and re.search(r'remove the higher tariff.{0,150}instead impose', decision.group(), re.I):
        return 'DECREASE', ''
    if re.search(r'^.{0,1100}(?:increase the respective tariff rates|increase .{0,60}from (?:an additional )?\d+ percent)', body, re.I):
        return 'INCREASE', ''
    if re.search(r'^.{0,220}increases in the duty rate.{0,80}from', body, re.I):
        return 'INCREASE', ''
    if re.search(r'all (?:imports of |steel articles imports|aluminum articles imports).{0,160}shall be subject to', body, re.I) and not re.search(r'Proclamation \d+.{0,120}(?:amended|revised)|is (?:further )?amended', body[:1400], re.I):
        return 'IMPOSE', ''
    if not re.search(r'tariff|duties|duty|HTSUS', body, re.I):
        return '', 'NO_TARIFF_ACTION'
    if re.search(r'removal of the additional duty|tariffs? .{0,90}(?:revoked|terminated)|(?:revoke|terminate).{0,90}(?:tariff|duties)', body, re.I):
        return 'REVOKE', ''
    if re.search(r'(?:reduce|decrease|lower)(?:d|s)? .{0,70}(?:duty|tariff|rate)|(?:duty|tariff|rate).{0,70}(?:reduced|decreased|lowered)', body[:2500], re.I):
        return 'DECREASE', ''
    if re.search(r'(?:increase|raise)(?:d|s)? .{0,70}(?:from|to)\s+\d+(?:\.\d+)?\s*percent|(?:duty|tariff|rate).{0,70}increased', body[:2500], re.I):
        return 'INCREASE', ''
    if re.search(r'(?:suspend|suspension).{0,100}(?:tariff|duties|duty)', body[:2500], re.I):
        return 'SUSPEND', ''
    if re.search(r'(?:extend|extension).{0,100}(?:tariff|duties|duty)', body[:2500], re.I):
        return 'EXTEND', ''
    if re.search(r'to establish a tariff.rate quota|shall be exempt from the duty|(?:duty|HTSUS|tariff).{0,100}(?:amended|modified|revised)|(?:amend|modify|revise).{0,100}(?:duty|HTSUS|tariff)', body, re.I):
        if re.search(r'quantitative limitation', body, re.I) and not re.search(r'shall be subject to|except|tariff.rate quota', body, re.I):
            return '', 'QUOTA_OR_RELIEF_ONLY'
        return 'SCOPE_CHANGE', ''
    if re.search(r'shall be subject to (?:an? )?(?:additional )?\d+(?:\.\d+)? percent|(?:impose|imposing).{0,80}(?:additional duties|ad valorem|tariff)', body, re.I):
        return 'IMPOSE', ''
    return '', 'NO_CLEAR_OPERATIVE_TARIFF_ACTION'


def dates(body, notes):
    matches = []
    for m in re.finditer(DATE, body, re.I):
        before = body[max(0, m.start()-330):m.start()]
        if re.search(r'(?:shall be|are|is|become|becomes) effective', before, re.I) and re.search(r'HTSUS|dut(?:y|ies)|tariff|entered|consumption', before, re.I):
            priority = 0
        elif re.search(r'(?:on or after|effective (?:on|as of)|beginning)\b', before[-150:], re.I) and re.search(r'dut(?:y|ies)|tariff|entered|consumption', before, re.I):
            priority = 1
        else:
            continue
        if re.search(r'comment|reporting|submit|request for relief', before[-160:], re.I):
            continue
        date = datetime.strptime(re.sub(r',?\s+', ' ', m.group(0)), '%B %d %Y').date().isoformat()
        matches.append((priority, m.start(), date))
    if not matches:
        notes.append('No explicit effective date attached to the duty extracted')
        return ''
    candidates = sorted(matches)
    chosen = candidates[0][2]
    # An amended schedule without a current effective clause can restate old dates.
    if candidates[0][0] == 1 and re.search(r'as follows:\s*\([a-zivx]+\)|from all countries except', body, re.I) and len({x[2] for x in matches}) > 1:
        notes.append('Multiple schedule dates without an unambiguous current duty-effective clause: ' + '; '.join(sorted({x[2] for x in matches})))
        return ''
    others = sorted({x[2] for x in matches} - {chosen})
    if others:
        notes.append('Other duty/schedule dates: ' + '; '.join(others))
    return chosen


def rates(body, action, notes, text):
    patterns = [r'(\d+(?:\.\d+)?)\s*percent\s+ad valorem', r'ad valorem tariff of\s+(\d+(?:\.\d+)?)\s*percent', r'shall be subject to an?\s+(\d+(?:\.\d+)?)\s*percent tariff', r'(?:additional\s+)?(?:ad valorem\s+)?rate of duty of\s+(\d+(?:\.\d+)?)\s*(?:percent|%)',
                r'(\d+(?:\.\d+)?)\s*(?:percent|%)\s+ad valorem(?:\s+rate of duty|\s+tariff)?',
                r'additional\s+(\d+(?:\.\d+)?)\s*(?:percent|%)\s+(?:duties|duty|tariff)']
    found = []
    for pattern in patterns:
        for m in re.finditer(pattern, body, re.I):
            if re.search(r'dut(?:y|ies)|tariff', body[max(0,m.start()-100):m.end()+100], re.I):
                found.append((m.start(), format(float(m.group(1)), 'g')))
    values = sorted({v for _, v in found}, key=float)
    transition = re.search(r'(?:increase(?:d)?|raised|reduced|decreased|lowered)(?: the respective tariff rates)?\s+from\s+(?:an additional )?(\d+(?:\.\d+)?)\s*percent(?: ad valorem)?\s+to\s+(?:an additional )?(\d+(?:\.\d+)?)\s*percent', body, re.I)
    decision = re.search(r'I have determined that.{0,700}', text, re.I)
    main_rate = re.search(r'(\d+(?:\.\d+)?) percent ad valorem tariff', decision.group(), re.I) if decision else None
    if action == 'REVOKE':
        chosen = ''
        notes.append('Revocation has no explicit replacement additional rate; removed or historical rates: ' + '; '.join(values))
    elif main_rate:
        chosen = format(float(main_rate.group(1)), 'g')
    elif transition:
        chosen = format(float(transition.group(2)), 'g')
    elif len(values) == 1:
        chosen = values[0]
    else:
        chosen = ''
        if values:
            notes.append('Main additional rate ambiguous; operative rates: ' + '; '.join(values))
    if not chosen and not values:
        notes.append('No explicit additional ad valorem rate extracted from operative text')
    if chosen and len(values) > 1:
        notes.append('Other operative rates: ' + '; '.join(v for v in values if v != chosen))
    increase = 'true' if transition and float(transition.group(2)) > float(transition.group(1)) else ''
    if action == 'INCREASE':
        increase = 'true'
    elif action == 'IMPOSE':
        increase = 'false'
    elif action == 'DECREASE':
        increase = 'false'
    if not increase:
        notes.append('Whether an existing rate increased is unclear or not applicable')
    return chosen, increase


def partners(body, notes):
    result = set()
    for clause in re.split(r'(?<=[.;])\s+|\([a-zivx]+\)', body):
        if not re.search(r'imports?|articles|countries|dut(?:y|ies)|tariff|except|exempt', clause, re.I):
            continue
        for name, pattern in COUNTRIES.items():
            for m in re.finditer(r'\b(?:' + pattern + r')\b', clause, re.I):
                preceding = clause[:m.start()]
                exempt = bool(re.search(r'\bexcept\b[^.;]*$', preceding, re.I) or re.search(r'shall be exempt from (?:the )?duty', clause, re.I))
                if exempt or re.search(r'(?:from|of|imports|articles|countries|tariff.rate quota)\b', preceding, re.I):
                    result.add(('EXCEPT:' if exempt else '') + name)
    if not result:
        notes.append('No named subject or exempt partners extracted; all-country coverage is not a country name')
    return ';'.join(sorted(result))


def codes(text, notes):
    found = set(re.findall(r'(?<![\d.])\d{4}\.\d{2}(?:\.\d{2})?(?:\.\d{2})?(?![\d.])', text))
    for m in re.finditer(r'\b(?:HTS(?:US)?|subheadings?|headings?)\s+(?:\d+.?digit level as:\s*)?((?:\d{4,10}(?:\s*(?:,|and|through)\s*)?)+)', text, re.I):
        found.update(x for x in re.findall(r'\b\d+\b', m.group(1)) if len(x) in (4,6,8,10))
    chapters = sorted({x[:2] for x in found})
    if re.search(r'\bthrough\b', text) and found:
        notes.append('HTS range endpoints retained; unlisted intermediate codes not inferred')
    if not found:
        notes.append('No HTS codes extracted')
    return ';'.join(sorted(found)), ';'.join(chapters)


def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cached-documents', help='Comma-separated cache snapshot; omitted documents count as missing text')
    args = parser.parse_args()
    records = json.loads((ROOT/'fr_index.json').read_text(encoding='utf-8'))
    assert len(records) == 2792, f'Expected 2792 index records, found {len(records)}'
    available = set(args.cached_documents.split(',')) if args.cached_documents is not None else {p.stem for p in (ROOT/'raw').glob('*.txt')}
    kept, rejected, missing = [], [], 0
    for record in records:
        path = ROOT/'raw'/(record['document_number']+'.txt')
        if record['document_number'] not in available or not path.is_file():
            missing += 1
            continue
        text = clean(path.read_text(encoding='utf-8', errors='replace'))
        body = operative(text)
        action, reason = classify(record, text, body)
        if reason:
            rejected.append(dict(document_number=record['document_number'], title=record['title'].replace('\u2014','-'), reason=reason))
            continue
        notes = []
        auth, note = authority(text)
        if note:
            notes.append(note)
        date_source = 'signing_date' if record.get('signing_date') else 'publication_date'
        notes.append('Announcement date uses ' + date_source)
        effective = dates(body, notes)
        rate, increase = rates(body, action, notes, text)
        partner = partners(body, notes)
        hts, chapters = codes(text, notes)
        absent = sum((auth == 'UNKNOWN', not effective, not rate))
        notes.append('HTS codes cover the full document and may include historical references; partners may have conditional or time-limited coverage')
        kept.append(dict(document_number=record['document_number'], title=record['title'].replace('\u2014','-'), doc_type=record['type'], agency=';'.join(a.get('raw_name','') for a in record.get('agencies',[])), authority=auth, action_kind=action, announcement_date=record.get(date_source) or '', effective_date=effective, rate_pct=rate, is_increase=increase, partners=partner, hts_codes=hts, hs_chapters=chapters, url=record.get('html_url') or '', confidence=['HIGH','MEDIUM','LOW'][min(absent,2)], notes=' | '.join(notes)))
    assert len(kept) + len(rejected) + missing == len(records) == 2792
    write_csv(ROOT/'tariff_events.csv', FIELDS, kept)
    write_csv(ROOT/'tariff_events_rejected.csv', ['document_number','title','reason'], rejected)
    print(f'Rows kept: {len(kept)}\nRows rejected: {len(rejected)}')
    for label, counts in [('Rejected by reason', Counter(x['reason'] for x in rejected)), ('Authority', Counter(x['authority'] for x in kept)), ('Action kind', Counter(x['action_kind'] for x in kept)), ('Confidence', Counter(x['confidence'] for x in kept)), ('Documents per year (kept, announcement date)', Counter(x['announcement_date'][:4] for x in kept))]:
        print(label + ':')
        for key, value in sorted(counts.items()):
            print(f'  {key}: {value}')
    print(f'No cached text: {missing}\nAccounting assertion: {len(kept)} + {len(rejected)} + {missing} = 2792 (passed)')


if __name__ == '__main__':
    main()
