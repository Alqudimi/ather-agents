# تدقيق الأرشيف وتصميم فرق OpenCode v2

## ما جرى تسليمه

أعيد تنظيم الملفات الصالحة إلى **621 ملف agent** ضمن **14 مجموعة**: 606 ملفات بوضع `subagent` (605 مفعّلة وملف اختبار واحد معطّل)، و14 قائداً بوضع `all`، ومنسّقاً عاماً واحداً بوضع `primary` فوق فرق التخصص الـ14. يوجد بذلك 620 ملفاً مفعّلاً وملف واحد معطّل. أُعيد استخدام أربعة من قادة المصدر، وأضيف عشرة قادة فرق جدد ومنسّق عام واحد. من 610 ملفات المصدر الصالحة، بقيت الملفات بعد تطبيعها، ثم أضيفت الملفات الجديدة وعددها أحد عشر. تحوي الحزمة فهرس CSV يربط الملفات المصدرية بمعرّفات الوكلاء الجديدة.

يوضح OpenCode v2 أن ملفات الوكلاء Markdown توضع في `~/.config/opencode/agents/` أو `.opencode/agents/`، وأن المجلدات المتداخلة تدخل في معرّف الوكيل. كما أن الوكيل المخصص يكون `primary` افتراضياً عند غياب `mode`، لذلك تم التصريح بـ`mode` لكل ملف بدلاً من الاعتماد على الافتراضات. [1] [3]

## بنية المجموعات

| المجموعة | القائد | ملفات الوكلاء |
|---|---|---:|
| `agent-systems` | `agent-systems/agent-systems-lead` | 40 |
| `architecture` | `architecture/chief-systems-architect` | 21 |
| `frontend` | `frontend/frontend-team-lead` | 53 |
| `backend` | `backend/backend-team-lead` | 13 |
| `data` | `data/data-team-lead` | 59 |
| `ai-ml` | `ai-ml/ai-ml-team-lead` | 99 |
| `security` | `security/cyber-security-orchestrator` | 50 |
| `quality` | `quality/master-architect-orchestrator` | 91 |
| `platform` | `platform/platform-team-lead` | 46 |
| `performance` | `performance/performance-engineering-manager` | 51 |
| `languages` | `languages/language-team-lead` | 31 |
| `product` | `product/product-team-lead` | 14 |
| `documentation` | `documentation/documentation-team-lead` | 21 |
| `specialized-domains` | `specialized-domains/domain-specialists-lead` | 31 |

توزيع الوكلاء آليّ-مساعد، اعتماداً على أسماء الملفات وقواعد أسبقية معلنة في أداة البناء، ثم تم تثبيت الحدود بصلاحيات تفويض صريحة. لذلك ينبغي التعامل مع الحدود القريبة بين التخصصات على أنها تصنيف تشغيلي قابل للتعديل، لا تصنيف علمي وحيد صحيح. راجع `AGENT-MANIFEST.csv` لتغيير أي عضو يدوياً.

## الحقائق الرسمية التي حكمت التصميم

- `mode: primary` هو وكيل الجلسة الرئيسي؛ `mode: subagent` يعمل فقط كجلسة فرعية؛ و`all` يسمح بالاثنين. قادة الفرق الـ14 بوضع `all` حتى يستدعيهم المنسّق العام كأبناء مع بقائهم قابلين للاختيار مباشرة؛ المنسّق العام بوضع `primary`. [1]
- أداة التفويض في v2 هي `subagent`؛ لا تستخدم ملفات القيادة القديمة `task` بوصفها أداة OpenCode الحالية. العمق الافتراضي مستوى واحد يمنع الطفل من تفويض مستوى إضافي. دليل ترحيل V2 ينص على أن المفتاح الجذري `subagent_depth` من V1 يُتجاهل، وأن المفتاح الصحيح هو `experimental.subagent_depth`; القيمة 2 تتيح مستوى إضافياً واحداً، وهو مطلوب لكي يفوض قائد يعمل كطفل إلى اختصاصيي فريقه. [1] [4] [6]
- جلسة الطفل تبدأ بسياق جديد، وتُستخدم صلاحيات الطفل المهيأة له لا صلاحيات الأب. لهذا تلزم كل مهمة مفوضة بسياق كامل ومحدد، ولا يصح افتراض وجود ذاكرة مشتركة أو أن المدير يفرض سياساته على الطفل. [1] [2]
- قواعد الصلاحيات هي قائمة مرتبة `{action, resource, effect}`، وآخر قاعدة مطابقة هي التي تفوز. لكل مدير قاعدة تمنع التفويض افتراضياً ثم استثناءات تسمح فقط بمعرّفات أعضاء فريقه؛ هذا يقيد من يستطيع القائد تشغيله لكنه **لا يضيق صلاحيات الأدوات الداخلية للطفل**. [1] [2]
- تنص وثائق v2 على عدم استخدام مفاتيح الواجهة القديمة مثل `temperature`, `top_p`, `prompt`, `permission`, `tools`, `disable`, و`maxSteps` في ملفات v2 الجديدة؛ وتستخدم بعض إعدادات الطلب `request` عند الحاجة. تمت إزالة الحقول القديمة غير المطابقة من الـfrontmatter؛ ونُقلت قيم `temperature` و`top_p` الرقمية إلى `request.body`، كما حُوّل `max_steps` إلى `steps` وفق دليل الترحيل. نُقلت خرائط `permission` البسيطة إلى `permissions` حيث أمكن تفسيرها دون تخمين. [1] [6]
- ملف المشروع يكتشف الوكلاء داخل `.opencode/agents`; لم يتم تضمين `default_agent` ولا صلاحيات جذرية في الحزمة حتى لا تغير سلوك المشروع بصمت. وثائق التهيئة تؤكد أن تغيير `default_agent` لا يغير الوكيل المخزن في جلسة موجودة. [3]

## ملاحظات جودة المصدر

لم يُثبّت Model بعينه: تفضيل الوكيل الفرعي غير المحدد يرث Model جلسة الأب، واختيار قائد أساسي لا يغيّر Model الجلسة المخزّن. لم يُفرض مزود أو Model غير معلوم التوفر في مشروع المستخدم. [1] [7]

- عُثر على **7 ملفات وكيل فارغة تقريباً (بايت واحد)**: `api-security.md, data-viz-engineer.md, db-optimizer.md, db-schema-designer.md, federated-learning-engineer.md, time-series-deep-learning-engineer.md, ultra-unit-test-agent.md`. حفظت في `quarantine/incomplete-agent-files/` خارج مسار اكتشاف OpenCode النشط، ولم تُنشأ لها تعليمات تخمينية.
- الوكيل `specialized-domains/simple-responder` fixture خاص باختبارات التقييم يرد بنص ثابت ولا يؤدي عملاً تخصصياً؛ احتُفظ به مع `disabled: true` وأزيل من قائمة تفويض قائد مجموعته.
- ملف `DETAILED_REPORT.md` مصدره يصف **491 ملفاً بتاريخ 13 يونيو 2026**، بينما الحزمة الحالية تتضمن 620 ملف Markdown. احتُفظ به فقط كمصدر تاريخي وليس كإحصاء حديث.
- ملف `README.md` الأصلي يقدم فهرساً مختصراً لبعض الوكلاء، لا فهرساً شاملاً للمجموعة الحالية؛ حُفظ باسم `docs/source-readme.md`.
- ملف `neural_security_architecture.md` وثيقة عربية مفاهيمية لا ملف وكيل؛ احتُفظ به ضمن `docs/`. عبارات مثل “التعلم والتكيف المستمر” و“قاعدة معرفية ديناميكية” ليست وظائف يضمنها مجرد تعريف Markdown أو سلوك OpenCode.
- وجود التزامات رقمية عامة في بعض المطالبات، مثل دقة أو نسب إنجاز مضمونة، لا يثبت تحقيقها؛ لا يجوز للقادة الجدد الادعاء بضمان نتائج أو تشغيل فحوص لم تتم.
- تمت المحافظة على أجسام تعليمات معظم الوكلاء الصالحين لتجنب إسقاط معرفة المجال. لم يُجر تدقيق بشري كامل لكل ادعاء متخصص داخل **621** مطالبة؛ لذلك لا ينبغي اعتبار وجود الوكيل اعتماداً مهنياً أو مصدراً موثوقاً بذاته.

## التثبيت والتحقق

1. فك الحزمة في مجلدها ثم شغّل `python3 scripts/install-opencode-v2.py install --project /path/to/project`؛ السكربت ينسخ الملفات إلى `.opencode/agents/`، يثبّت OpenCode V2 الرسمي عند الحاجة، ويضبط `experimental.subagent_depth: 2` دون استبدال الإعدادات الأخرى.
2. نفّذ `python3 scripts/install-opencode-v2.py verify --project /path/to/project`. يستخدم التحقق `opencode debug agents` الخاص بـV2 ويطابق الملفات بايتاً ببايت.
3. اختُبر OpenCode v2.0.32 في HOME ومشروعين مؤقتين: طابقت الملفات الـ621، وسجّل runtime جميع معرّفات الوكلاء الـ620 المفعّلة، وتحقق السكربت من قيمة إعداد V2.
4. جُرّب `uninstall` في حالة إعداد جديد وحالة ملف مشروع موجود: أزيلت ملفات الحزمة غير المعدّلة، وحُذف الإعداد الجديد أو استُعيد القديم بايتاً ببايت، وأزيل CLI المثبّت من السكربت عبر uninstaller الرسمي؛ بقيت ملفات sentinel والإعداد العام غير التابعة للحزمة.
5. لم يُجر اختبار نموذج فعلي يتطلب مزوداً وبيانات اعتماد. تحقق اكتشاف runtime لا يثبت صحة كل إجابة تخصصية ولا يثبت إجراء مهمة تفويض متداخلة مدعومة بمزود.

## المراجع الرسمية

[1] يشرح أنماط primary/subagent/all، مواقع ملفات الوكلاء، صيغ الإعداد، وصلاحيات اختيار الوكيل الفرعي وسياق الجلسة.

[2] يشرح صيغة قواعد الصلاحيات وترتيب مطابقتها وحقيقة أن الطفل يستخدم صلاحياته الخاصة.

[3] يشرح أماكن ملفات الإعداد ودمجها واختيار `default_agent`.

[4] يشرح أداة `subagent` وحدود عمق التعشيش.

## References

[1]: https://opencode.ai/v2/docs/agents/ "OpenCode v2 Agents documentation"
[2]: https://opencode.ai/v2/docs/permissions/ "OpenCode v2 Permissions documentation"
[3]: https://opencode.ai/v2/docs/config/ "OpenCode v2 Config documentation"
[4]: https://opencode.ai/v2/docs/tools/ "OpenCode v2 Tools documentation"
[5]: https://opencode.ai/config.json "OpenCode configuration JSON Schema"
[6]: https://opencode.ai/v2/docs/migrate-v1/ "OpenCode v2 Migration from V1 documentation"
[7]: https://opencode.ai/v2/docs/models/ "OpenCode v2 Models documentation"
[8]: https://opencode.ai/docs/config/ "OpenCode configuration and subagent depth"
[9]: https://github.com/anomalyco/opencode/issues/43748 "V2 config schema drift, including experimental.subagent_depth"
