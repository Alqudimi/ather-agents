# Brand specification — Ather Agents

- **Artifact:** موقع ثابت ثنائي اللغة لمشروع أدوات المطورين Ather Agents، يعمل على GitHub Pages.
- **Audience:** مطورو OpenCode v2 الذين يريدون تثبيت حزمة الوكلاء واستخدامها وصيانتها.
- **Visual language:** واجهة أدوات مطور تحريرية هادئة، تباين واضح ومساحات محسوبة، مع إبراز الشعار المعدني الأصلي.
- **Mode:** تصميم جديد لموقع تعريفي ثابت. لا تعدل سلوك مثبت الوكلاء.
- **Dials:** visual variance 5/10، motion intensity 3/10، information density 6/10، asset dependence 2/10، brand fidelity 7/10.
- **Primary brand hex:** `#5865F2` كما اختاره المستخدم.
- **Logo:** الأصل الذي قدمه المستخدم موجود في `site/assets/brand/ather-agents-logo.png`؛ خلفيته سوداء. استخدمه دون رسم بديل أو تعديل بكسلاته.
- **Brand accent from supplied logo:** برتقالي دافئ تقريبي `#F86830` مأخوذ من البكسلات البرتقالية اللامعة، ويستخدم كإشارة ثانوية فقط.
- **Typography:** عناوين serif تحريرية مع خطوط النظام المتاحة؛ متن عربي/لاتيني بخطوط نظام محلية، والشفرة بخط monospace.
- **Layout:** صفحة ثابتة RTL افتراضياً مع تبديل لغة واتجاه، مقسمة إلى hero، أوامر التثبيت، بنية فريق الوكلاء، مجالات الفريق، الضمانات، والأسئلة الشائعة.
- **Motion:** GSAP 3.15.0 عبر CDN مثبت الإصدار؛ استخدام `gsap.utils` للظهور التدريجي والتفاعل. الحركة اختيارية ومتوقفة عند `prefers-reduced-motion`.
- **Accessibility:** semantic HTML، focus واضح، أهداف لمس 44px أو أكبر، ألوان مدققة، وإتاحة المحتوى دون GSAP.
