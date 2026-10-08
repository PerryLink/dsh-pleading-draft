# dsh-pleading-draft — वाद-पत्र के तत्वों की सूची की पूर्णता की जाँच, प्रत्येक दावे की एक पंक्ति

`dsh-pleading-draft` वाद-पत्र (अथवा आवेदन) के तत्वों की सूची पढ़ता है — मुकदमे का शीर्षक और प्रत्येक दावे की एक पंक्ति, जिसमें `序号`、`诉讼请求`、`事实依据`、`证据`、`法律依据`、`金额`、`期限` कॉलम होते हैं — और उसी दस्तावेज़ की पूर्णता तथा आंतरिक सुसंगति की जाँच करता है: क्या प्रत्येक दावे का तथ्य-आधार दर्ज है, साक्ष्य की ओर संकेत है और विधिक आधार लिखा है, क्या राशि वाले दावे में पालन-अवधि भी दर्ज है, क्या शीर्षक में वादी और प्रतिवादी के नाम हैं, क्या कोई क्रमांक दोहराया नहीं गया है, और क्या दावा-कॉलम में कोई भरा न गया टेम्पलेट प्लेसहोल्डर शेष है।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| दावा लिखा गया है, पर साक्ष्य कॉलम किसी ओर संकेत नहीं करता। | `PL-002` उस पंक्ति को दर्ज करता है जिसका `证据` कॉलम साक्ष्य की ओर संकेत नहीं करता: यह देखता है कि संदर्भ लिखा है, यह नहीं कि साक्ष्य मौजूद है, पूरा है या उसी दावे से संबंधित है। |
| विधिक आधार कॉलम में केवल «संबंधित उपबंध» जैसा सामान्य वाक्य लिखा है। | `PL-003` हर दावे के तत्व में `法律依据` कॉलम भरा होने की अपेक्षा करता है। खाली कॉलम दर्ज होता है; यह नहीं जाँचता कि उद्धृत उपबंध मौजूद है, प्रभावी है या इस मामले पर लागू होता है। |
| राशि लिखी है, पर पालन-अवधि दर्ज नहीं है। | `PL-004` केवल तब चलता है जब `金额` कॉलम भरा हो, और तब `期限` कॉलम की अपेक्षा करता है: अवधि के बिना राशि दर्ज होती है। केवल घोषणात्मक दावे से ऐसी अवधि नहीं माँगी जाती जो उसमें नहीं है। राशि का हिसाब सही है या अवधि उचित है, यह नहीं जाँचा जाता। |
| मुकदमे के शीर्षक में कौन-कौन से क्षेत्र होने चाहिए? | `PL-005` शीर्षक में वादी और प्रतिवादी के नाम की अपेक्षा करता है; दोनों कॉन्फ़िगरेशन क्षेत्र हैं, इसलिए आपका अपना प्रपत्र वाद-कारण और विचारणीय न्यायालय भी जोड़ सकता है। यह नहीं जाँचता कि पक्षकार इस दावे के लिए सही हैं या नहीं। |
| यदि दावा-कॉलम में अब भी टेम्पलेट प्लेसहोल्डर रह गया हो तो क्या होता है? | `PL-007` उसे दर्ज करता है: यह जिन शब्दों को खोजता है वे हैं `【`, `】`, `{{`, `}}`, `XXX`, `xxx`, `待填`, `待补充`, `TBD`, `todo` और `示例`। इनमें से कोई शब्द न रखने वाला अस्पष्ट दावा पास हो जाता है, क्योंकि दावे की अपेक्षित स्पष्टता का निर्णय विधिक निर्णय है। |
| कोई नियम कुछ दर्ज करने के बजाय `skipped` में दिखता है। क्या इसका अर्थ है कि वह पास हो गया? | नहीं। `skipped` उस जाँच का नाम है जो चली ही नहीं: उदाहरण के लिए `PL-002` वहाँ तब आता है जब वह कॉन्फ़िगरेशन में बंद थी, `only` चयन से बाहर रह गई, अथवा सामग्री उसकी पूर्व-शर्त पूरी करती थी और कोई अंतर नहीं मिला। जो जाँच चलती ही नहीं, वह किसी कॉलम को पास नहीं करा सकती, और उसकी सीमा वही रहती है: वह कभी नहीं देखती कि साक्ष्य पर्याप्त है या दावे से मेल खाता है। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
|---|---|---|
| 《中华人民共和国民事诉讼法》 | 1991年通过，经 2007、2012、2017、2021、2023 年五次修正（现行条号据 2021 年第四次修正及 2023 年第五次修正文本核对） | PL-001, PL-002, PL-003, PL-004, PL-005, PL-006, PL-007 |

**Boundary:** this plugin checks a **起诉状（或申请书）要素核对表** for completeness — that every claim records
its factual basis, points at evidence, states its legal basis, that a monetary claim states an amount and a
performance deadline, that the document names both parties, that element numbers are unique, and that no
placeholder survives. It does **not** decide whether a claim will succeed, whether it is time-barred, whether
jurisdiction is right, whether the evidence suffices, or whether the case should be accepted. **Those are the
court's determinations and the advocate's substantive judgement.**

> ### ⚠️ What this plugin can and cannot do
>
> **It reads a checklist, not the pleadings, the evidence or the statutes.** So it can only check that a
> column *points at* evidence or *names* a provision — **never that the evidence suffices or that the
> provision exists, is in force, or applies**. `PL-002` and `PL-003` say so in their own notes. Test the
> plugin against a pleading whose cited article was repealed: it will pass, because looking up statutes is a
> different job and one this plugin deliberately does not do.
>
> **Every `excerpt` in the rule pack says, in so many words, that the clause text was not obtained.** The
> regime lives in 《中华人民共和国民事诉讼法》(notably its article on what a statement of claim must record)
> and the Supreme People's Court's interpretation of it. The verification pass could not retrieve verbatim
> clause text, so the pack states the gap in the `excerpt` field itself and keeps every rule at `warn` or
> `info`. **When the texts are in hand, replace each `excerpt` with the real clause and raise `kind` to
> `direct`.**
>
> `PL-004` fires only when an amount column is filled, so a claim for a declaration or for a change of legal
> relation is not asked for a performance deadline it does not have. And `PL-007` catches placeholders only:
> a claim that is vague **without** containing `【】` or `待填` will pass, because judging whether a claim is
> stated with the required precision is a legal judgement.

## Compatibility

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-pleading-draft
dsh --profile <name> --dump-config | grep 'dsh-pleading-draft'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/pleading-draft.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-pleading-draft
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-pleading-draft contributors.
