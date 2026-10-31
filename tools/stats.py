"""تقرير موحّد لتقدم الجلستين (claude + opencode): stats/STATS.md و stats/stats.json
آمن للتشغيل من أي أحد في أي وقت (يكتب في stats/ فقط، ويعيد توليد الملفين كاملين)."""
import json, sys, time, difflib
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pbzlib

WHO = {"claude": "Claude", "opencode": "opencode", "review2": "المراجعة النهائية"}
SCOPE = {"claude": "الحوارات والقراءات والمهمات والفصول", "opencode": "الواجهة والعناصر والأسلحة والأوصاف", "review2": "كل النصوص (قراءة ثانية)"}


def bar(p, n=20):
    k = round(p * n); return "█" * k + "░" * (n - k)


def lines(p):
    try: return sum(1 for l in p.read_text(encoding="utf8").splitlines() if l.strip() and not l.startswith("#"))
    except OSError: return 0


def collect(who, orig):
    w = pbzlib.ROOT / "work" / who
    batches = sorted((w / "batches").glob("batch_*.json"))
    s = dict(who=who, batches=len(batches), done=0, entries=0, chars=0, entries_done=0, chars_done=0,
             changed=0, accepted=0, rejected=0, warned=0, size=Counter(), fam=Counter(), pending_next=None, last_done=None)
    for b in batches:
        items = json.loads(b.read_text(encoding="utf8"))
        s["entries"] += len(items); s["chars"] += sum(len(i["text"]) for i in items)
        o = w / "out" / b.name
        if not o.exists():
            s["pending_next"] = s["pending_next"] or b.name; continue
        s["done"] += 1; s["last_done"] = b.name
        s["entries_done"] += len(items); s["chars_done"] += sum(len(i["text"]) for i in items)
        base = {i["key"]: i["text"] for i in items}
        try: out = json.loads(o.read_text(encoding="utf8"))
        except ValueError: s["rejected"] += 1; continue
        for k, t in out.items():
            if k not in orig: s["rejected"] += 1; continue
            err, warn = pbzlib.validate(orig[k], t)
            if err: s["rejected"] += 1; continue
            s["accepted"] += 1; s["warned"] += bool(warn)
            if k in base and t != base[k]:
                s["changed"] += 1; s["fam"][k.split("_")[0]] += 1
                r = difflib.SequenceMatcher(None, base[k], t).ratio()
                s["size"]["طفيف (تنوين/إملاء/ترقيم)" if r >= .93 else "متوسط (كلمات)" if r >= .75 else "إعادة صياغة"] += 1
    s["extras"] = {n: lines(w / n) for n in ("glossary_proposals.md", "questions.md", "skipped.md")}
    st = w / "STATE.md"
    s["state_mtime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(st.stat().st_mtime)) if st.exists() else "—"
    return s


def main():
    orig = pbzlib.load_original().texts()
    data = [collect(w, orig) for w in WHO]
    now = time.strftime("%Y-%m-%d %H:%M")
    tot = lambda k: sum(d[k] for d in data)
    pe = tot("entries_done") / max(tot("entries"), 1)
    md = [f"# إحصاءات المراجعة الموحّدة\n\nآخر تحديث: {now} · يُولَّد بـ `python tools/stats.py`\n",
          f"## الإجمالي\n\n`{bar(pe)}` **{pe:.1%}** — {tot('entries_done'):,} من {tot('entries'):,} مدخلة · "
          f"{tot('done')}/{tot('batches')} دفعة · معدَّل مقبول: **{tot('changed'):,}** · مرفوض: **{tot('rejected')}**\n",
          "| الجلسة | النطاق | الدفعات | المدخلات المراجَعة | المعدَّل | نسبة التعديل | مرفوض | تحذيرات | آخر STATE |",
          "|---|---|---|---|---|---|---|---|---|"]
    for d in data:
        rate = d["changed"] / d["entries_done"] if d["entries_done"] else 0
        md.append(f"| {WHO[d['who']]} | {SCOPE[d['who']]} | {d['done']}/{d['batches']} | {d['entries_done']:,}/{d['entries']:,} | "
                  f"{d['changed']:,} | {rate:.1%} | {d['rejected']} | {d['warned']} | {d['state_mtime']} |")
    for d in data:
        p = d["entries_done"] / max(d["entries"], 1)
        md += [f"\n## {WHO[d['who']]}\n", f"`{bar(p)}` {p:.1%} · الدفعة التالية: `{d['pending_next'] or 'انتهت'}` · آخر منتهية: `{d['last_done'] or '—'}`\n"]
        if d["size"]:
            md.append("**نوع التعديل:** " + " · ".join(f"{k}: {v}" for k, v in d["size"].most_common()) + "\n")
        if d["fam"]:
            md.append("**أكثر الفئات تعديلًا:** " + " · ".join(f"`{k}` {v}" for k, v in d["fam"].most_common(8)) + "\n")
        e = d["extras"]
        md.append(f"**ملفاتها:** مقترحات مسرد {e['glossary_proposals.md']} سطر · أسئلة {e['questions.md']} · متروك {e['skipped.md']}\n")
    md.append("\n> نسبة تعديل عالية جدًا (> 30%) مع كثرة «إعادة صياغة» إشارة إلى مبالغة في إعادة الكتابة: يراجعها صاحب المشروع.\n")
    out = pbzlib.ROOT / "stats"; out.mkdir(exist_ok=True)
    (out / "STATS.md").write_text("\n".join(md), encoding="utf8")
    (out / "stats.json").write_text(json.dumps({"updated": now, "sessions": [{**d, "size": dict(d["size"]), "fam": dict(d["fam"])} for d in data]},
                                              ensure_ascii=False, indent=1), encoding="utf8")
    print("\n".join(md[:8]))


if __name__ == "__main__":
    main()
