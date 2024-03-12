---
title: Team
nav:
  order: 3
  tooltip: About our team
---

# {% include icon.html icon="fa-solid fa-users" %}Team

{% include section.html %}

## Current Members
{% include list.html data="members" component="portrait" filters="role: pi" %}
{% include list.html data="members" component="portrait" filters="role: ^(?!pi$)" %}

{% include section.html %}


## Alumni
- Sha Hu, PhD, 2010-2015, Southwest University
- Jinxiu Li, Master, 2014-2017, Agricultural Bank of China

{% include grid.html style="square" content=content %}
