# دليل تثبيت OpenCode v2 وحزمة الوكلاء

## الخلاصة الحاسمة

الإعداد الذي يفعّل سلسلة التفويض المطلوبة `orchestrator → team lead → specialist` في OpenCode v2 هو:

```json
{
  "experimental": {
    "subagent_depth": 2
  }
}
```

**لا تستخدم** `"subagent_depth": 2` في جذر JSON على أنه إعداد V2؛ دليل الترحيل الرسمي يقول إن الحقل الجذري القديم مقبول في V1 لكنه **يُتجاهل في V2**، ويطلب استخدام `experimental.subagent_depth`. العمق الافتراضي مستوى واحد، والرقم 2 يسمح بمستوى متداخل إضافي واحد؛ لا يسمح بمستوى ثالث. [3] [5]

## تثبيت الحزمة وتشغيلها

1. ثبّت OpenCode v2 بنفسك أولاً من [الموقع الرسمي](https://opencode.ai/v2/docs/). مثبّت الوكلاء **لا يثبت OpenCode ولا يزيله**، ويتوقف برسالة واضحة إذا لم يجد الإصدار v2.
2. من مجلد المشروع المستهدف شغّل الأمر الموحد:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- install
   ```

3. لاستهداف مشروع آخر، أضف `--project /absolute/path/to/project`. يلزم Bash وcurl وtar وPython 3.9+. ينسخ السكربت الوكلاء إلى `<project>/.opencode/agents/` ويضبط `experimental.subagent_depth: 2` في ملف الإعداد الفعّال. لا يغير `default_agent` ولا صلاحيات المشروع العامة.
4. تحقق من الملفات ومن اكتشاف OpenCode الفعلي:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- verify
   ```

   قبل التثبيت يتحقق السكربت من عدد الملفات، ومعرّفاتها، وأحجامها وبصمات SHA-256 في `AGENT-MANIFEST.csv`. ثم ينفذ `opencode debug agents`، وهو أمر V2، ويطابق الملفات الـ621 بايتاً ببايت ويتأكد أن كل معرّف مفعّل ظاهر في runtime وأن fixture المعطّل غير ظاهر. يلزم أن يكون المسار مشروعاً يتعرف إليه OpenCode؛ إذا ظهرت قائمة فارغة، تحقق من جذر المشروع ومكان تشغيل OpenCode. السكربت لا ينشئ مستودع Git نيابة عنك.

### عدم تعديل إعداد JSONC

السكربت يحرر **JSON الصارم فقط** حتى لا يفسد التعليقات أو الفواصل المسموح بها في JSONC. إذا كان الملف الفعّال JSONC أو كان هناك ملفان متعارضان في مستوى الأسبقية نفسه، يوقف التعديل بأمان. عند الحاجة يمكنك تثبيت الوكلاء دون تعديل العمق:

```bash
curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- install --no-depth-2
```

ثم ادمج المثال `opencode.subagent-depth-2.example.jsonc` يدوياً في الإعداد الفعّال، ولا تستبدل ملفاً موجوداً به. في ترتيب V2، ملف `.opencode/opencode.json(c)` يتقدم على ملف `opencode.json(c)` المباشر؛ لذلك يفضّل السكربت ملف `.opencode` إذا وجد واحداً. [4]

## إزالة التثبيت والتراجع

من مجلد الحزمة:

```bash
curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- uninstall
```

- يحذف السكربت فقط ملفات الوكلاء التي أضافها والتي ما زالت مطابقة لبصماتها وقت التثبيت.
- يحذف إعداد `experimental.subagent_depth` الذي أنشأه إذا لم يتغير، أو يستعيد إعداد المشروع السابق بايتاً ببايت إذا كان قد عدّله.
- إذا وجد أن المستخدم عدّل ملفاً أضافه السكربت أو غيّر الإعداد بعد التثبيت، يحافظ على الملف المتغير ويترك سجل الحالة ليتعامل معه المستخدم؛ لا يحذفه تخميناً.
- لا يحذف الإلغاء OpenCode CLI أو أي تثبيت خارجي؛ المثبّت يدير ملفات الوكلاء وإعداد المشروع فقط.

## التحقق والسلوك

يحتوي المثبّت على تحقق من ملف manifest (621 ملف وكيل وبصمات SHA-256)، وفحص إصدار OpenCode v2، واكتشاف runtime عبر `opencode debug agents` في أمر `verify`. كما أُجريت اختبارات صياغة Bash وPython واختبار رفض في HOME معزول عند غياب OpenCode؛ توقّف التثبيت برسالة تطلب من المستخدم تثبيت V2 بنفسه ولم ينشئ ملفات في المشروع.

لم يُجر اختبار كامل باستخدام OpenCode v2 فعلي في هذه الجلسة. فحص `verify` يثبت مطابقة الملفات واكتشاف runtime، لكنه لا ينفذ مهمة نموذجية تستدعي قائداً ثم اختصاصياً، ولا يضمن نتيجة النموذج أو جودة كل ملف تخصصياً.

## نقطة مهمة بشأن المخطط والتحقق في المحررات

وثائق ترحيل V2 هي المرجع لإعداد التفويض: المفتاح الفعّال `experimental.subagent_depth`. لكن JSON Schema المنشور حالياً على `opencode.ai/config.json` لا يتطابق تماماً مع توثيق V2؛ بل أُبلغ رسمياً عن هذا التأخر، ومن أمثلته أن أدوات التحقق قد ترفض `experimental.subagent_depth` رغم أن إعداد V2 هو المطلوب. لذلك لا يضع السكربت رابط `$schema` في ملف إعداد جديد كي لا يصنع تحذيراً مضللاً، ولا يعتمد على المخطط المنشور للتحقق من هذا الحقل. هذا **اختلاف في التحقق بالمحررات**، وليس سبباً لاستبدال المفتاح الصحيح بمفتاح V1 الذي تتجاهله V2. [3] [8] [9]

## مصادر OpenCode الرسمية

1. [OpenCode v2: Getting Started / Installation](https://opencode.ai/v2/docs/) — قناة V2 وطريقة تثبيت CLI.
2. [تعليمات تثبيت OpenCode v2 الرسمية](https://opencode.ai/v2/docs/) — على المستخدم تثبيت CLI بنفسه؛ لا يستدعيه مثبّت الوكلاء.
3. [OpenCode v2: Migrate from V1](https://opencode.ai/v2/docs/migrate-v1/) — يبين أن top-level `subagent_depth` يُتجاهل، وأن البديل هو `experimental.subagent_depth`؛ كما يحذر من تعارض تثبيت V1 المدار بحزم.
4. [OpenCode v2: Config](https://opencode.ai/v2/docs/config/) — مواقع الملفات، ترتيب دمجها وأسبقية إعداد `.opencode`.
5. [OpenCode v2: Agents](https://opencode.ai/v2/docs/agents/) و[Tools](https://opencode.ai/v2/docs/tools/) — أوضاع الوكلاء وصلاحيات الأداة والحد الافتراضي للتعشيش.
6. [OpenCode v2: CLI commands](https://opencode.ai/v2/docs/cli/commands/) — مرجع أوامر التشخيص والإزالة.
7. [مرجع إعداد عام](https://opencode.ai/docs/config/#subagent-depth) — يشرح العمق في شكل الإعداد القديم؛ لا تتقدم هذه الصيغة على توجيه الترحيل الخاص بـV2.
8. [بلاغ اختلاف JSON Schema عن توثيق V2](https://github.com/anomalyco/opencode/issues/43748) — تفاصيل عن الحقول التي يقبلها runtime لكن المخطط المنشور لا يواكبها.
9. [JSON Schema المنشور](https://opencode.ai/config.json) — يُذكر هنا لتوضيح مصدر تحذير المحررات، لا باعتباره المرجع الأعلى من تعليمات V2.
