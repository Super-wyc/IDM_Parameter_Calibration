#set page(paper: "a4", numbering: "1")
#set text(size: 12pt, font: ("Times New Roman", "Source Han Serif SC"))
// 用的思源宋体，没有字体的话可以安装一下，typst目前宋体不支持原生加粗
#set par(justify: true)
#show heading.where(level:1): set text(size: 14pt)
#set math.equation(numbering: "(1)", supplement: [Eq.])

#let indent = v(2em)+h(1em)
// 每段首行缩进加indent

#align(center, text(size: 14pt, [*基于HighD数据的IDM跟驰模型标定*]))

#align(center)[#text()[]]

#indent 本次作业···