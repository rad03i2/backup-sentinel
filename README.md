# Backup Sentinel

Safe, local, versioned directory backups with SHA-256 verification and guarded restore.

**Author:** Radwan Abdulhadi Ahmed · رضوان عبدالهادي أحمد · GitHub: @rad03i2

## English

### Overview
Backup Sentinel is a small, auditable Python backup tool for creating self-contained snapshots of a directory. Every file is hashed before copying and verified after copying. Each snapshot carries a JSON manifest, can be verified later, and can be restored only after passing integrity checks.

### Why it exists
Backups should be boring and predictable. Backup Sentinel favors explicit commands, local storage, cryptographic integrity checks, and refusal to overwrite existing restore targets unless the user opts in.

### Features
- Versioned, timestamped snapshots; previous snapshots are never modified.
- SHA-256 before/after copy verification.
- `verify` detects missing or changed backup files.
- Guarded restore refuses corrupted snapshots and existing destination files by default.
- Atomic per-file restore through a temporary file followed by `os.replace`.
- Hidden files are excluded by default and may be included explicitly.
- Symbolic links are not followed.
- Source and backup repository may not overlap, preventing recursive backups.
- Machine-readable JSON output and a small Python API.
- No network access, accounts, telemetry, or secrets.

### Requirements & installation
Python 3.10+ is required.

```bash
git clone https://github.com/rad03i2/backup-sentinel.git
cd backup-sentinel
python -m pip install .
```

For development:

```bash
python -m pip install -e ".[dev]"
```

### Usage
Create a snapshot:

```bash
backup-sentinel create ./important ./my-backups
```

Include hidden files when needed:

```bash
backup-sentinel create ./important ./my-backups --include-hidden
```

List snapshots and copy a `snapshot_id`:

```bash
backup-sentinel list ./my-backups
```

Verify before relying on a backup:

```bash
backup-sentinel verify ./my-backups 20260920T100000.000000Z
```

Restore to an empty/new destination:

```bash
backup-sentinel restore ./my-backups 20260920T100000.000000Z ./restored
```

Existing files are protected. Use `--overwrite` only when intentional.

### Python API
```python
from pathlib import Path
from backup_sentinel import create_snapshot, verify_snapshot

manifest = create_snapshot(Path("important"), Path("backups"))
status = verify_snapshot(Path("backups"), manifest["snapshot_id"])
assert status["ok"]
```

### Repository format
Each snapshot is self-contained:

```text
my-backups/
└── snapshots/
    └── <snapshot-id>/
        ├── manifest.json
        └── data/
            └── ... original relative paths ...
```

The manifest records relative path, byte size, and SHA-256 for every file.

### Project structure
```text
src/backup_sentinel/core.py   backup, verification, restore engine
src/backup_sentinel/cli.py    command-line interface
src/backup_sentinel/__init__.py public API
tests/test_backup.py          end-to-end safety tests
.github/workflows/ci.yml      cross-platform CI
```

### Testing
```bash
ruff check .
pytest
```
CI runs the same checks on Ubuntu, Windows, and macOS with Python 3.10, 3.12, and 3.13.

### Preview / screenshots
This is intentionally a CLI utility. The JSON output from `create`, `list`, `verify`, and `restore` is the canonical preview and is suitable for scripts and terminals; no graphical UI is implemented.

### Security & privacy
All work is local. The tool does not encrypt backup contents, so protect the backup destination with appropriate OS permissions or disk encryption. SHA-256 detects corruption/tampering but is not authentication against an attacker who can modify both data and manifest. See `SECURITY.md`.

### Limitations
- Snapshots are full copies, not deduplicated or incremental.
- No compression, encryption, remote/cloud transport, scheduler, or retention pruning is built in.
- Files changing while a snapshot is being created may cause verification failure; retry after writes stop.
- File metadata preservation is limited to what `shutil.copy2` and the host filesystem support.

### Optional roadmap
Content-addressed deduplication and explicit retention policies are reasonable future additions, provided the current safety model remains intact.

### Contributing & license
See `CONTRIBUTING.md`. Released under the MIT License; see `LICENSE`.

### Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

## العربية

### نظرة عامة
Backup Sentinel أداة بايثون محلية لإنشاء نسخ احتياطية بإصدارات مستقلة للمجلدات. تحسب الأداة بصمة SHA-256 لكل ملف قبل نسخه وتتحقق منه بعد النسخ، وتحفظ بيان JSON لكل لقطة يمكن فحصه لاحقًا قبل الاستعادة.

### لماذا هذا المشروع؟
الهدف هو جعل النسخ الاحتياطي واضحًا وقابلًا للتدقيق: أوامر صريحة، تخزين محلي، تحقق من سلامة البيانات، وعدم استبدال ملفات الاستعادة الموجودة إلا بموافقة المستخدم.

### المميزات
- لقطات زمنية مستقلة لا تعدّل النسخ السابقة.
- تحقق SHA-256 أثناء إنشاء النسخة.
- أمر `verify` لكشف الملفات المفقودة أو المتغيرة داخل النسخة الاحتياطية.
- رفض استعادة لقطة تالفة تلقائيًا.
- حماية الملفات الموجودة في وجهة الاستعادة افتراضيًا.
- كتابة آمنة أثناء الاستعادة باستخدام ملف مؤقت ثم الاستبدال الذري.
- تجاهل الملفات المخفية افتراضيًا مع خيار تضمينها.
- عدم اتباع الروابط الرمزية.
- منع تداخل مجلد المصدر مع مستودع النسخ لتجنب النسخ الدائري.
- مخرجات JSON وواجهة Python برمجية صغيرة.
- لا اتصال بالإنترنت ولا حسابات ولا تتبع ولا مفاتيح سرية.

### المتطلبات والتثبيت
يتطلب Python 3.10 أو أحدث.

```bash
git clone https://github.com/rad03i2/backup-sentinel.git
cd backup-sentinel
python -m pip install .
```

للتطوير والاختبار:

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```

### الاستخدام
إنشاء لقطة:

```bash
backup-sentinel create ./important ./my-backups
```

عرض اللقطات:

```bash
backup-sentinel list ./my-backups
```

فحص سلامة لقطة:

```bash
backup-sentinel verify ./my-backups <snapshot-id>
```

استعادة لقطة:

```bash
backup-sentinel restore ./my-backups <snapshot-id> ./restored
```

لن تستبدل الأداة ملفًا موجودًا في وجهة الاستعادة إلا عند إضافة `--overwrite` صراحةً. ولتضمين الملفات المخفية أثناء إنشاء النسخة استخدم `--include-hidden`.

### الإعدادات وبنية التخزين
لا تحتاج الأداة إلى متغيرات بيئة أو ملف `.env`. تُحفظ كل لقطة تحت `snapshots/<snapshot-id>/` وبداخلها `manifest.json` ومجلد `data/` الذي يحافظ على المسارات النسبية الأصلية.

### هيكل المشروع
الكود الأساسي في `src/backup_sentinel/core.py`، وواجهة الأوامر في `cli.py`، والاختبارات في `tests/test_backup.py`، وإعداد CI في `.github/workflows/ci.yml`.

### الاختبارات
تغطي الاختبارات إنشاء النسخ، التحقق، الاستعادة، الملفات المخفية، اكتشاف العبث، تعارض ملفات الاستعادة، منع تداخل المسارات، وصحة بيان JSON. ويعمل CI على Linux وWindows وmacOS.

### المعاينة
المشروع أداة سطر أوامر ولا يحتوي واجهة رسومية. مخرجات JSON هي الواجهة المقصودة للاستخدام البشري والبرمجي.

### الأمان والخصوصية
كل العمليات محلية. النسخ **غير مشفرة**، لذلك يجب حماية وسيط التخزين بصلاحيات النظام أو تشفير القرص عند الحاجة. SHA-256 يكشف تغير البيانات لكنه لا يمنع مهاجمًا لديه صلاحية تعديل البيانات والبيان معًا. راجع `SECURITY.md`.

### القيود
النسخ الحالية كاملة وليست incremental أو deduplicated، ولا توجد ميزات سحابية أو ضغط أو تشفير أو جدولة أو حذف تلقائي للنسخ القديمة. وقد تفشل عملية التحقق إذا تغير ملف المصدر أثناء النسخ، وفي هذه الحالة يُنصح بإعادة المحاولة بعد توقف الكتابة.

### التطوير المستقبلي الاختياري
يمكن مستقبلًا إضافة إزالة التكرار المبنية على المحتوى وسياسات احتفاظ صريحة دون التضحية بنموذج الأمان الحالي.

### المساهمة والترخيص
راجع `CONTRIBUTING.md`. المشروع مرخص بترخيص MIT الموجود في `LICENSE`.

### المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
