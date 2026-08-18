# Emergence Lab — Implementation Specification v0.2 (frozen)

Dit document is de **normatieve** implementatiespecificatie. Waar dit document een regel vastlegt, mag de code daar niet van afwijken.

Milestone 1 is geïmplementeerd. Milestone 2 begint bij **C3** (lokale LLM via configureerbare Ollama-adapter). Wereldregels van v0.2 blijven frozen (m1-v2). Wijzigingen aan food/regen/C2-features = nieuwe experimentversie.

---

## 1. Projectdoel

Bouw een klein, reproduceerbaar experimenteel platform in Python om te onderzoeken:

> **Hoeveel complexe en emergente gedragingen kunnen ontstaan uit een zeer eenvoudige digitale wereld, en hoe verandert dat gedrag wanneer de controllerconfiguratie van individuele organismen wordt vervangen?**

Dezelfde wereld, organismen, observaties, acties en fysica moeten gebruikt kunnen worden met verschillende decision controllers.

De experimentele interventie is de **controllerconfiguratie**. Alle overige wereld- en organismemechanica blijven constant, tenzij expliciet als ablation gedefinieerd. Controllercondities mogen verschillen in controller-interne staat (genome, memory) alleen waar de experimentele matrix dat toestaat.

Controllers krijgen dezelfde **raw** Observation (5×5 + energy + age). Ze gebruiken die niet noodzakelijk hetzelfde. C1 redeneert over de volle lokale geometrie. C2 projecteert naar 9 lineaire features (geen diagonalen, geen afstand, geen eigen energy in het genotype). C3 serialiseert de patch naar een prompt. **Effective representation is onderdeel van de controllerconditie.** Zeg niet dat C1 vs C2 “alleen het decision mechanism” is.

**Reproductie is in de hoofdmatrix geen universele wereldregel.** C2/C5/C6 mogen reproduceren; C0/C1/C3/C4 niet. Dat is een controller-conditieverschil, geen puur decision-mechanism-effect. Interpreteer C2-versus-C0 daarom niet als “alleen de decision function veranderde”. Zie §10.1.

Dit is een **mechanistisch artificial-life model, geen biologisch model**. De wetenschappelijke waarde zit in de gevolgen van de gespecificeerde rekenregels, niet in biologische realisme-claims.

De simulator programmeert geen antwoord op de onderzoeksvraag. Hij creëert alleen een omgeving waarin het antwoord **gemeten** kan worden.

De eerste implementatie blijft **bewust minimaal**. Geen onnodige frameworks, databases, distributed systems of complexe agentarchitecturen.

---

## 2. Centrale architectuur

```text
WORLD
  │
  │ observation
  ▼
ORGANISM
  │
  │ observation
  ▼
CONTROLLER
  │
  │ Decision {action, memory_write?, rationale?}
  ▼
WORLD
```

De controller is verwisselbaar.

```text
                    SAME WORLD
                        │
                    SAME BODY
                        │
                 SAME OBSERVATION
                        │
                    SAME ACTIONS
                        │
                 ┌──────┴──────┐
                 │ CONTROLLER  │
                 └─────────────┘
```

**Fundamentele regels:**

1. Een controller krijgt **nooit** een World-object. Alleen een immutable Observation (plus, indien de conditie dat toestaat: eigen genome en/of eigen memory).
2. Een controller mag geen informatie gebruiken die zijn experimentconditie niet toestaat.
3. Wall-clock tijd (inclusief LLM-latency) is **geen** simulatie-tijd. Een tick is een discrete simulatie-eenheid. Latency is alleen een metric.
4. Controllers mogen verschillen in intern decision mechanism en inductive bias. Het experiment meet gedragsgevolgen van het vervangen van de controller, niet rekenkracht onder identieke objectieven.
5. Gebruik in wetenschappelijke tekst deze termen strikt:
   - **population dynamics** — birth, death, populatiegrootte
   - **genetic evolution** — erfelijk genome + mutatie + selectie
   - **individual lifetime memory** — persistente, agent-specifieke informatie
   - **pretrained computation** — LLM als vaste decision function
   C0 zonder genome kan populatiedynamiek hebben (in ablation C0-R) zonder genetic evolution. Memory ≠ learning.

---

## 3. Milestones

Houd alle zeven controllers in de matrix, maar implementeer ze niet in één keer.

### Milestone 1 — Artificial Life

Wereld, logging, replay, renderer, analytics-pipeline.

- C0 Random
- C1 Reactive
- C2 Evolutionary

Na deze milestone moet het experiment **zonder enige LLM-dependency** werken.

### Milestone 2 — LLM

- C3 LLM
- C4 LLM + Memory

### Milestone 3 — Hybrid

- C5 LLM + Evolution
- C6 LLM + Evolution + Memory

### Milestone 4 — Online learning (niet v0.1)

- C7 Online learning
- C8 LLM + Online learning

Zie §29 voor latere research-fasen (individuality, self-model, social). Die horen niet in de eerste matrix.

Verification-controllers (`AlwaysStay`, `AlwaysNorth`) horen in tests, niet in de experimentele matrix.

---

## 4. World semantics (normatief)

Dit hoofdstuk is bindend. Twee implementaties die dit volgen, moeten bij dezelfde seed en dezelfde niet-LLM-controller **bit-identieke** runs produceren.

### 4.1 Raster

```text
width  = 32
height = 32
```

Discreet 2D-raster. Geen continue physics, zwaartekracht, temperatuur, dag/nacht, gebouwen, wapens, communicatie of handel.

### 4.2 Torus

De wereld is **toroidal**. Randen wrappen:

```text
x = (x + dx) mod width
y = (y + dy) mod height
```

Er zijn geen muren. `available_actions` is daardoor altijd de volledige action space.

### 4.3 Occupancy

Iedere cel bevat op ieder moment hoogstens:

```text
EMPTY
RESOURCE          # resource-site met food aanwezig
ORGANISM          # precies één organisme
```

Harde regels:

- **Precies één organisme per cel.**
- Een organisme en een resource staan **nooit** tegelijk op dezelfde cel. Betreden van een resource-cel consumeert de resource in dezelfde tick (§4.8).
- Resource-sites zonder food zijn `EMPTY` (de site-identiteit blijft in de wereldconfig bestaan, zie §4.6).

### 4.4 Simultane tick (harde invariant)

```text
All decisions for tick T are based exclusively on world state T.
```

**Nooit** sequentieel:

```text
organisme A beweegt → B observeert de nieuwe wereld → B beweegt
```

Per tick:

```text
observe (iedereen, op state T)
   ↓
all controllers decide
   ↓
all actions collected
   ↓
conflicts resolved
   ↓
all movements applied
   ↓
rest van de wereldupdate
```

Deze invariant hoort in de tests.

### 4.5 Tick-pipeline (vaste volgorde)

Iedere tick, in deze volgorde, onafhankelijk van controller-type:

```text
1.  begin tick
2.  resource regen (patches)
3.  create observations          # world state T na regen; memory-staat is die van einde T−1
4.  controllers decide           # iedere decide → Decision; volgorde van aanroep mag state niet veranderen
5.  validate actions
    invalid → STAY + INVALID_ACTION; memory_write mag blijven
6.  resolve movement conflicts
7.  execute movements            # log MOVE of MOVE_BLOCKED
8.  auto-consume resources
9.  apply energy
10. process death
11. process reproduction (indien conditie reproductie toestaat)
12. increment age van levende organismen
13. apply memory_write           # pas nu; zichtbaar vanaf tick T+1, nooit in dezelfde decide
14. log events
15. snapshot if required
16. next tick
```

De aanroepvolgorde van controllers mag de wereld niet beïnvloeden. Sorteer organismen intern altijd op `organism_id` als je itereert.

### 4.6 Resources — vaste patches + cooldown

Resources zijn **geen** live-random regen tijdens de run.

**Model A (verplicht in v0.1):**

- Bij world-generatie (tick 0) worden `resource_count` **vaste sites** gekozen.
- Die posities zijn identiek voor alle controller-clones van dezelfde seed.
- Opeten verwijdert de food; de site blijft bestaan.
- Food respawnt op **dezelfde** cel na een cooldown, en **alleen** als de cel vrij is.

Defaults:

```text
resource_count    = 20
resource_value    = 30
regen_delay       = 15   # ticks after consumption
```

Respawn-regel, iedere tick in stap 2 van de pipeline:

```text
voor iedere site:
    als de cel geen resource heeft
    én de cel geen organisme heeft
    én (tick - last_consumed_tick) >= regen_delay
        → plaats resource
```

`last_consumed_tick` start als `-regen_delay` voor sites die op tick 0 food hebben, zodat initiële food geldig is en na eerste consumptie de cooldown ingaat.

**Geen spawn als er een organisme op de cel staat.** Campen op een patch levert geen automatische oogst op. Na eten moet het organisme weg om respawn mogelijk te maken. Staan op een lege site is strikt nadelig (metabolisme, geen instroom).

Geen `EAT`-actie. Consumptie is automatisch bij betreden (stap 8), of niet, als de cel bezet blijft tot na regen — regen gebeurt dan niet.

### 4.7 Energy

Twee aparte kosten:

```text
base_metabolism = 1
movement_cost   = 1
```

Per tick, in stap 9, voor ieder levend organisme dat de tick heeft overleefd tot deze stap:

```text
STAY:  energy -= base_metabolism              # −1
MOVE:  energy -= base_metabolism + movement_cost  # −2
```

Een **geblokkeerde** of **ongeldige** move telt als `STAY` (alleen `base_metabolism`).

Na een geslaagde move op een resource-cel, in stap 8 vóór stap 9:

```text
energy += resource_value   # +30
```

`energy <= 0` na stap 9 → dood in stap 10.

`STAY` is een echte beslissing: bewegen kost meer, maar kan food opleveren.

### 4.8 Movement en collisions

Acties:

```text
MOVE_NORTH
MOVE_SOUTH
MOVE_EAST
MOVE_WEST
STAY
```

**Geen swaps, geen “in iemands gat springen”.** Een organisme mag alleen bewegen naar een cel die **aan het begin van de tick** (na regen, vóór movement) geen organisme bevat.

Resolutie:

1. Ieder organisme declareert een doelcel (`STAY` → huidige cel).
2. Ongeldige actie → doelcel = huidige cel, event `INVALID_ACTION`.
3. Move naar een cel die op T een organisme bevat → mislukt, blijft staan, telt als `STAY` voor energy. Log `MOVE_BLOCKED`.
4. Meerdere organismen claimen dezelfde **lege** cel → **uniforme loting** onder de pretenders. Eén winnaar beweegt. De rest blijft staan (energy als `STAY`). Log `MOVE_CONFLICT` (pretenders + winnaar). Gebruik niet de naam `COLLISION`: er is geen fysiek contact, alleen een geclaimde cel.
5. Geen ID-priority. Geen energy-priority.
6. Iedere **geslaagde** verplaatsing is een world mutation. Log verplicht:

```text
MOVE
    organism_id
    from
    to
```

Loting moet **reproduceerbaar** zijn en **niet** via een sequentiële RNG-stroom (anders divergeert de wereld-RNG zodra de ene controller wél een conflict heeft en de andere niet).

Verplichte hash (stabiel over processen; **niet** Python `hash()`):

```python
import hashlib

def conflict_winner(seed: int, tick: int, x: int, y: int, ids: list[int]) -> int:
    ids_sorted = sorted(ids)
    material = f"{seed}:{tick}:{x}:{y}:{','.join(map(str, ids_sorted))}"
    digest = hashlib.sha256(material.encode("ascii")).digest()
    idx = int.from_bytes(digest[:8], "big") % len(ids_sorted)
    return ids_sorted[idx]
```

Zelfde seed + tick + cel + pretender-set ⇒ zelfde winnaar.

### 4.9 Reproductie

**Hoofdmatrix:** uitgeschakeld voor C0, C1, C3, C4. Ingeschakeld voor C2, C5, C6.

Dat is een bewuste experimentele factor, geen verborgen wereldregel. C2 verschilt van C0 in decision mechanism **én** in populatiedynamiek. Claims van de vorm “evolutionary decision-making caused this” zijn pas geldig na de ablation in §10.1.

Defaults:

```text
reproduction_energy_threshold = 150
reproduction_cost             = 75
```

Alleen in stap 11, na energy en death. Alleen levende organismen.

**Kind erft de controllerconditie van de ouder.** Nooit opnieuw loten of uit de run-config trekken:

```text
child.controller_condition = parent.controller_condition
```

Voor C2/C5/C6: genome inherited + mutatie.  
Voor geplande ablations zonder genome (C0-R, C1-R, C3-R, C4-R): geen genome, geen mutatie, kind krijgt dezelfde controllerconditie. Memory wordt **nooit** geërfd.

Procedure per ouder, gesorteerd op `organism_id`:

1. `energy >= 150` anders skip (geen kosten).
2. Verzamel **lege 4-connected buren** (N, S, E, W; torus). Geen diagonalen. Een buur met resource (geen organisme) telt als leeg van occupancy en is een geldige geboortecel.
3. Geen lege buur → geen reproductie, geen kosten.
4. Kies één doelcel via dezelfde klasse hash (niet sequentiële RNG):

```python
def pick_index(seed: int, tick: int, parent_id: int, n: int) -> int:
    material = f"{seed}:{tick}:{parent_id}:birth:{n}"
    digest = hashlib.sha256(material.encode("ascii")).digest()
    return int.from_bytes(digest[:8], "big") % n
```

Buren in vaste volgorde: North, East, South, West.

5. Als twee (of meer) ouders dezelfde doelcel kiezen: **uniforme loting** onder die ouders met `conflict_winner(seed, tick, x, y, parent_ids)`. Alleen de winnaar plant. Verliezers houden hun energy en krijgen dit tick geen kind.
6. Winnaar: `parent.energy -= 75`. Kind krijgt `energy = 75`. Geen kind spawnen en daarna doden.
7. Kind-velden:

```text
nieuwe organism_id            # monotoon oplopend, nooit hergebruikt
position                      # gekozen buurcel
energy                        = 75
age                           = 0
alive                         = True
parent_id                     = parent.id
generation                    = parent.generation + 1
controller_condition          = parent.controller_condition
genome                        = mutate(parent.genome)  # alleen als de conditie genome heeft
memory                        = leeg                   # nooit geërfd
```

8. **Newborn consume (normatief, één pad):** na plaatsing, in dezelfde reproductiestap: als de geboortecel een resource bevat, consumeert het kind onmiddellijk.

```text
birth
  ↓
child appears (energy = 75)
  ↓
if resource present:
    child.energy += resource_value    # 75 + 30 = 105
    resource verdwijnt
    last_consumed_tick = tick
```

Er is geen tweede toegestane interpretatie. Test dit expliciet.

### 4.10 Death

`energy <= 0` → `alive = False`, cel wordt `EMPTY`. Geen lijken. Age van doden wordt niet meer verhoogd. Doden nemen niet deel aan collisions of reproductie.

### 4.11 Initiële plaatsing (tick 0)

Gegenereerd uit `world_rng` (zie §16), daarna **immutable** in de snapshot.

```text
initial_population = 10
resource_count     = 20
```

Regels:

- Alle resource-sites op unieke cellen.
- Alle organismen op unieke cellen.
- **Geen organisme op een resource-site** (geen stille maaltijd op tick 0).
- Ieder organisme start met `energy = 100`, `age = 0`, `generation = 0`, `parent_id = None`.
- Voor C2/C5/C6: initiële genomes uit `evolution_rng` (§9.4), opgeslagen in de snapshot.

Deze tick-0-staat is identiek voor alle controller-clones van dezelfde seed. Over seeds heen verschilt de layout.

### 4.12 Energiebudget (verplicht tunen, niet gokken)

Ruwe drager-capaciteit:

```text
inflow   ≈ resource_count × resource_value / regen_delay
         = 20 × 30 / 15
         = 40 energy / tick

Optimal single-patch harvest cycle (eat, step off, wait, step on) is approximately:

    resource_value − regen_delay − 2  =  30 − 15 − 2  =  +13

v0.2 defaults (value 20, delay 25) made that cycle negative (−7), so even C1 could not reach the reproduction threshold. These defaults are experiment version **m1-v2**.

verbruik ≈ populatie × (1 bij STAY, 2 bij MOVE)
```

Met 10 organismen:

- allemaal `STAY` → 10/tick → surplus als patches vrij blijven
- allemaal `MOVE` → 20/tick → tekort
- occupancy blokkeert respawn → effectieve inflow lager

Doel van de default: C0 sterft niet instant uit, C2 kan meerdere generaties halen, food is schaars genoeg voor concurrentie. Elke wijziging van deze getallen is een **nieuwe experimentversie**.

---

## 5. Organisme

Alle condities gebruiken hetzelfde lichaam. Optionele velden bestaan in de datastructuur maar zijn alleen actief in de corresponderende conditie en zitten **niet** in de observation tenzij §7 dat toestaat.

```text
id
position
energy
age
alive
parent_id              # None voor founders
generation             # 0 voor founders
controller_condition   # geërfd; nooit herlooted
genome                 # alleen C2, C5, C6
memory                 # alleen C4, C6
```

De controller ziet genome/memory alleen als de conditie dat toestaat, en alleen van **zichzelf**.

---

## 6. Action space

Iedereen dezelfde acties. Geen controller mag extra acties krijgen.

```text
MOVE_NORTH
MOVE_SOUTH
MOVE_EAST
MOVE_WEST
STAY
```

De simulator valideert iedere actie. Ongeldige output (verkeerd token, hallucinatie, timeout-parse):

```text
event: INVALID_ACTION
gedrag: STAY
energy: als STAY
```

Niet stilzwijgend naar een “dichtstbijzijnde geldige actie” corrigeren.

---

## 7. Observation

Iedere controller krijgt dezelfde observation-structuur. De observation is een **immutable** datastructure. De controller mag de wereld zelf niet inspecteren.

### 7.1 Egocentrisch, geen globale coördinaten

**Geen** globale `(x, y)`. **Geen** organism-IDs. **Geen** energy van andere organismen.

Default:

```text
observation_radius = 2   # 5×5 patch, torus-wrap
```

Inhoud:

```text
SELF:
    energy
    age

LOCAL 5×5:
    iedere cel ∈ {SELF, EMPTY, RESOURCE, ORGANISM}

available_actions   # op torus altijd de vijf acties; toch meegeven voor de LLM-interface
```

Voorbeeld (noorden = boven):

```text
. . . . .
. . F . .
. . A . .
. O . . .
. . . . .
```

```text
A = SELF
F = RESOURCE
O = ORGANISM
. = EMPTY
```

Het centrum is altijd `SELF`.

### 7.2 Voorbeeldstructuur

```python
Observation(
    energy=42,
    age=103,
    cells=...,          # 5×5 immutable, centrum = SELF
    available_actions=(MOVE_NORTH, MOVE_SOUTH, MOVE_EAST, MOVE_WEST, STAY),
)
```

Genome en memory worden **niet** in `Observation` gestopt. Die gaan als aparte, conditie-afhankelijke argumenten naar `decide` (zie §8).

---

## 8. Controller interface

Iedere controller, inclusief C0–C2, retourneert hetzelfde type. Memory-writes horen niet buiten `decide` te gebeuren.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Decision:
    action: Action
    memory_write: str | None = None
    rationale: str | None = None


class Controller:
    def decide(self, observation: Observation, *, genome=None, memory=None) -> Decision:
        ...
```

- C0/C1/C2: `memory_write=None`, `rationale=None`
- C0/C1/C3: `genome=None`, `memory=None`
- C2/C5: `genome` gezet, `memory=None`
- C4: `memory` gezet, `genome=None`
- C6: beide gezet

`memory_write` wordt toegepast aan het **einde** van tick T en is pas beschikbaar in `decide` op tick T+1. Nooit in dezelfde beslissing zichtbaar.

De engine geeft nooit meer mee dan de conditie toestaat. Ongeldige `action` → engine dwingt `STAY`; `memory_write` mag alsnog worden toegepast (FIFO, cap, max chars).

---

## 9. Controllers

### 9.1 C0 — Random (random-controller baseline)

Niet een absoluut null model: de wereldfysica, resources, metabolisme, torus en collisions blijven actief. In wetenschappelijke tekst: **random-controller baseline**, niet “null world”.

```text
action = choice(observation.available_actions)   # via controller_rng
```

De rest van de observation wordt genegeerd. `Decision.memory_write` en `rationale` zijn `None`.

`controller_rng` is **stateful binnen een run**. Als de populatie krimpt, volgen minder draws en schuift de stream. Dat is intentioneel en geen reproduceerbaarheidsschending: latere random events hangen af van seed **én** de geschiedenis van wie er leefde. Zelfde seed + zelfde geschiedenis ⇒ zelfde run.

Doel: vaststellen wat deze wereld plus een willekeurige decision function veroorzaakt.

### 9.2 C1 — Reactive

Geen leren, geen geheugen, geen genome, geen LLM. Vaste, extreem eenvoudige regelset. **Geen N-S-E-W prioriteitsbias.**

```text
1. Verzamel alle resource-cellen in de 5×5 (niet SELF).
2. Geen resource in zicht → uniforme random geldige actie (controller_rng).
3. Wel resource(s) → kies de dichtstbijzijnde in Manhattan-afstand op de egocentrische patch.
   Bij gelijke afstand: uniforme loting onder die cellen (controller_rng).
4. Zet één stap in een 4-connected richting die de Manhattan-afstand tot die cel verkleint.
   Bij twee even goede richtingen: loting (controller_rng).
```

Organismen in beeld worden genegeerd. Geen padfinding, geen geheugen van patches.

C1 is een **hand-coded, survival-relevante heuristic** (food-seeking). C3-A krijgt geen expliciet food-doel. Ze delen dezelfde observation, niet hetzelfde objectief of dezelfde inductive bias. Zeg later niet dat C1 en C3 “hetzelfde doel” kregen.

Doel: meten wat lokale perceptie plus een vaste food-seeking regel al oplevert.

### 9.3 C2 — Evolutionary

Geen handgemaakte strategie, geen neural net, geen exploratie-gen. Mutatie + selectie door de wereld is de enige “intelligentie”.

#### Features (9)

Uit de 5×5, centrum = eigen cel. Straal langs de as (twee cellen recht in die richting, torus in de lokale patch al gewrapt):

```text
resource_N = 1 als minstens één RESOURCE op (0, +1) of (0, +2) in egocentrische assen
resource_S = 1 als minstens één RESOURCE op (0, −1) of (0, −2)
resource_E = 1 als minstens één RESOURCE op (+1, 0) of (+2, 0)
resource_W = 1 als minstens één RESOURCE op (−1, 0) of (−2, 0)
organism_N / organism_S / organism_E / organism_W   # zelfde, voor ORGANISM
bias       = 1 altijd
```

Geen diagonalen in de features. `SELF` telt niet als `ORGANISM`. **Eigen energy en age zitten in de observation maar niet in het C2-genotype.** C2 kan daardoor niet evolutionair leren anders te handelen bij energy=5 versus energy=100. Dat is bewust: evolutie binnen een **constrained phenotype space**, niet “evolutie over de raw observation”. Niet verruimen in v0.1. Latere ablation: `C2 + own energy` / densere features.

Daardoor is C1 vs C2 geen zuivere “hand-coded vs evolved” vergelijking op dezelfde informatierijkdom. C1 ziet elke RESOURCE in de 5×5 (inclusief diagonalen) en heeft een ingebouwde food-prior. C2 ziet acht as-bits: N1 en N2 zijn één bit; een patch met alleen diagonale food is feature-identiek aan een lege patch (alleen `bias`). Dat is een handicap én de C2-conditie. **Niet achteraf features toevoegen omdat C2 faalt.** Een latere benoemde conditie (`C2-diag` / densere features) is een nieuwe experimentversie, geen stille spec-fix. Diagnostic in Milestone 1: vast cardinal-oracle-genome over **dezelfde** 9 features (`evolutionary_oracle`), plus een representability-rapport (C1-actie vs die 9 bits). Zie §10.2.

As-conventie in code: documenteer en test één mapping (bijv. row 0 = noord in de 5×5-print) en houd die overal aan.

#### Genome

```text
9 features × 5 acties = 45 weights
type: float
```

```text
score(action) = Σ_f  weight[action, f] × feature[f]
action        = argmax(score)
```

Bij gelijke max-score: uniforme loting onder de winnende acties via `controller_rng`.

Gewichten mogen negatief (afstoting ontstaat vanzelf). Geen softmax, geen extra random-exploratie-term.

#### Initieel genome (tick 0)

Iedere weight i.i.d. `Uniform(-0.1, 0.1)` uit `evolution_rng`. Alle founders krijgen **onafhankelijke** genomes. Die waarden zitten in de snapshot.

Niet allemaal nul: dan is C2 tot de eerste mutatie alleen tie-break-random.

#### Mutatie (geen crossover)

```text
mutation_probability = 0.05    # per weight
mutation_strength    = 0.1     # std van Gauss
```

```text
child_genome = copy(parent_genome)
voor iedere weight:
    met p=0.05 (evolution_rng):
        weight += Normal(0, mutation_strength)   # evolution_rng
```

Fitness is **niet** expliciet. Selectie ontstaat uit survival, energy en reproductie.

### 9.4 C3 — LLM

De LLM is uitsluitend een decision function. Adapter-patroon: de simulator kent het model niet. **Modelnaam, endpoint en parameters zijn configureerbaar, nooit hardcoded.**

Config: `llm.model`, `llm.endpoint`, `llm.temperature`, `prompt_id`. CLI: `--llm-model`, `--llm-endpoint`, `--prompt-id`. Default backend is lokaal **Ollama** (`http://127.0.0.1:11434`); andere OpenAI-achtige endpoints mogen later via dezelfde config, nooit een hardcoded modelnaam in de controllerklasse.

Controller-namen: `llm` / `llm_a` (prompt A), `llm_b` (prompt B). Geen genome, geen reproductie, geen memory. Elke Ollama-tag is een andere `experiment_id`.

Thinking-modellen (o.a. Qwen3.8, R1, QwQ): `think: false` in de request; `<think>`-tags strippen vóór parse. Self-reported rationale ≠ inner reasoning.

Input: Observation + available actions (+ prompt-template uit config).  
Output: een `Decision` met exact één `action` (plus optioneel `rationale` / bij C4 `memory_write`).

De LLM krijgt geen: world state, toekomst, IDs, globale coördinaten, tools, internet, Python, shell, memory, genome, andere agentstates buiten de 5×5.

Twee prompt-baselines (experimentconfig, niet hardcoded in de controllerklasse):

**LLM-A — minimal** (default voor C3 in de eerste reeks):

> Choose exactly one valid action based only on the observation. Reply with exactly one of: NORTH, SOUTH, EAST, WEST, STAY.

Geen survive, geen maximize energy, geen find food, geen reproduce.

**LLM-B — survival instructed** (ablation, zelfde wereld/clones):

> Your objective is to remain alive as long as possible. Choose exactly one valid action based only on the observation. Reply with exactly one of: NORTH, SOUTH, EAST, WEST, STAY.

LLM-A vs LLM-B is een ablation, geen extra permanente controller in de hoofmatrix.

Optioneel later, niet Milestone 2-verplicht: rationale vragen vs. alleen actie. Als rationale bestaat, heet het `self_reported_rationale` in de trace / `Decision.rationale` in de interface, **niet** chain-of-thought. Het is geen interne monoloog.

> Self-reported rationales are treated as behavioral outputs generated by the model, not as privileged access to the model's internal reasoning process.

Parse-falen of ongeldige actie → `INVALID_ACTION` + `STAY`. Raw output altijd bewaren (§18).

**Geen inference-cache** als stille optimalisatie. Cache zou C3 in een lookup-table veranderen. Alleen later als expliciete, gelogde conditie.

LLM-runs zijn alleen reproduceerbaar voor zover exact dezelfde model weights, quantisatie, inference backend, runtime-versie, hardware/software-configuratie en decoding-parameters behouden blijven. `temperature = 0` garandeert geen bit-identieke output over engines, GPU-kernels of modelreleases. Log minimaal: model file hash, quantisatie, backend, CUDA-versie, runtime-versie, sampling parameters.

### 9.5 C4 — LLM + Memory

Identiek aan C3, plus individueel geheugen.

```text
memory: list[str]
memory_capacity = 20
```

Geen embeddings, geen RAG, geen vector DB.

Controller-namen: `llm_memory` / `llm_a_memory` (prompt A + memory), `llm_b_memory` (prompt B + memory). Geen genome, geen reproductie. Memory wordt nooit geërfd.

De experimentele interventie is **persistente, agent-specifieke informatie**, niet “memory alleen”. C4 krijgt ook een langere prompt / meer tokens dan C3. Interpreteer verschillen niet als een zuiver geheugeneffect los van extra context.

C4-A en C4-B zijn dezelfde doelen als C3-A en C3-B. Extra: memory in de prompt, en optioneel één `MEMORY:`-regel. Geen food-doel, geen “onthoud patches”.

**C4-A** (default):

> Choose exactly one valid action based only on the observation and your memory. Reply with exactly one of: NORTH, SOUTH, EAST, WEST, STAY on the first line. Optionally add a second line MEMORY: <one short note to keep>. Omit MEMORY to write nothing.

**C4-B** (survival ablation):

> Your objective is to remain alive as long as possible. Choose exactly one valid action based only on the observation and your memory. Reply with exactly one of: NORTH, SOUTH, EAST, WEST, STAY on the first line. Optionally add a second line MEMORY: <one short note to keep>. Omit MEMORY to write nothing.

Daarna in beide: Observation-blok (zelfde serialisatie als C3) en `Memory:` (lege lijst → `(empty)`).

C4-configs gebruiken `num_predict = 128` (C3 blijft 64) zodat een korte memory-regel niet door de sampler wordt afgekapt. Dat is een sampling-limiet, geen extra intelligentie.

Timing (normatief):

```text
observe T
  ↓
read memory T          # writes van eerdere ticks
  ↓
decide → action + optional memory_write
  ↓
memory_write wordt toegepast aan einde tick T
  ↓
beschikbaar vanaf T+1
```

Nooit in dezelfde beslissing opnieuw zichtbaar.

Na iedere beslissing mag de LLM **één** string schrijven (ook bij invalid/fallback). Lege string of `None` = geen write. Te lange string: afkappen op een configureerbare `memory_entry_max_chars` (default 200). Bij overflow van de lijst: drop oldest (FIFO).

Memory bevat alleen wat dit organisme zelf schrijft. Niet geërfd. Gelogd per write.

### 9.6 C5 — LLM + Evolution

Genome uit §9.3 wordt als compacte context aan de LLM gegeven (bijv. de 45 weights of een korte samenvatting in de prompt). Het genome **dwingt geen actie af**. De LLM blijft de decision maker.

Reproductie en mutatie zoals C2.

### 9.7 C6 — LLM + Evolution + Memory

C5 + C4. Geen communicatie.

### 9.8 C7 — Online learning (documentatie, niet bouwen in v0.1)

Ontbreekt in de eerste matrix: een agent die tijdens zijn leven de decision function aanpast.

```text
population dynamics     ≠   genetic evolution
individual memory       ≠   learning
pretrained LLM          ≠   ontogenetic adaptation
```

C7 = ontogenetisch (bijv. minimaal RL). Pas Milestone 4. Niet in v0.1 bouwen.

---

## 10. Experimentele matrix (v0.1)

| ID | Controller | Genome | Memory | Reproduction | Milestone |
| --- | --- | --- | --- | --- | --- |
| C0 | Random | No | No | No | 1 |
| C1 | Reactive | No | No | No | 1 |
| C2 | Evolutionary | Yes | No | Yes | 1 |
| C3 | LLM (prompt A default) | No | No | No | 2 |
| C4 | LLM + Memory | No | Yes | No | 2 |
| C5 | LLM + Evolution | Yes | No | Yes | 3 |
| C6 | LLM + Evolution + Memory | Yes | Yes | Yes | 3 |

LLM-B (survival prompt) is een ablation op C3/C4, geen eigen ID in deze tabel.

Nieuwe capabilities (communicatie, object manipulation, culture, online learning, prompt evolution) horen niet in v0.1.

### 10.1 Reproductie is een experimentele factor

De hoofdmatrix blijft C0–C6 zoals hierboven. Reproductie wordt **niet** universeel aangezet in v0.1 (dat zou C0/C1-populatiedynamiek veranderen en LLM-condities duurder maken).

Na Milestone 1, vóór sterke C2-claims: **reproduction-without-adaptation** ablations. Named conditions, geen extra decision class:

```text
random_r      C0-R   Random + reproduction, geen genome, geen mutatie
reactive_r    C1-R   Reactive + reproduction, geen genome, geen mutatie
```

Later, optioneel en duur:

```text
C3-R   LLM + reproduction, geen genome
C4-R   LLM + Memory + reproduction, geen genome
```

Vraag die deze ablations beantwoorden:

> Is het verschil tussen C2 en C0 veroorzaakt door **genetic evolution van de controller**, of door **reproduction / population dynamics** (meer lichamen, meer concurrentie)?

C0-R/C1-R: kind krijgt `controller_condition` van de ouder, geen genome. CLI-namen: `random_r`, `reactive_r`.

### 10.2 Diagnostic: C2 phenotype vs C2 evolution

Niet in de hoofdmatrix. Doel: scheiden of C2 faalt omdat de 9-bit space C1-achtig foerageren niet kan uitdrukken, of omdat random-init + mutatie die phenotype niet vindt.

```text
evolutionary_oracle     zelfde 9 features en linear argmax als C2;
                        vast cardinal genome (resource op as → die kant);
                        geen mutatie, geen reproduction
evolutionary_oracle_r   zelfde decision class, reproduction aan, geen genome
```

Het oracle-genome is **geen** fitted kopie van C1 (diagonalen blijven onzichtbaar). Interpretatie:

- oracle ≈ C1 en random-C2 dood → bootstrap-falen in een wél bruikbare cardinal phenotype
- oracle ≪ C1 (vooral diagonal-only) → representatieplafond; dat is geen reden C2-features in v0.1 te verruimen
- oracle dood zoals C2 → zelfs de handgezette cardinal policy persist niet

CLI: `python -m emergence_lab representability` (geen batch). Daarna same-world clones op frozen m1-v2, zelfde seeds 1–100.

---

## 11. Seeds versus same-world clones

Twee lagen. Ze lossen twee verschillende problemen op.

### 11.1 Seed = welke wereld

De seed initialiseert world-generatie. Seed 1 en seed 77 zijn twee universums met **dezelfde regels** en **andere layout** (andere patch-posities, andere startposities, andere initiële genomes voor C2).

Claims over controllers moeten over veel seeds standhouden, niet op één toevallige kaart.

### 11.2 Clone = dezelfde wereld, andere controller

Voor **één** seed: genereer tick 0, bewaar een immutable snapshot, clone die snapshot, start iedere controller vanaf exact die staat.

```text
seed 1 → wereld W1 (tick 0) → snapshot
              │
    ┌─────────┼─────────┬─────────┐
    ▼         ▼         ▼         ▼
   C0        C1        C2        C3
```

Op tick 0 zijn posities, energy, age en resource-sites identiek. Daarna divergeren de runs omdat controllers andere acties kiezen. Dat divergeren is het experiment.

```text
                    seed 1 (= W1)                 seed 77 (= W77)
                          │                              │
          ┌───────┬───────┼───────┐              zelfde splitsing
          ▼       ▼       ▼       ▼
        C0      C1      C2      C3
```

| | Seed | Clone |
| --- | --- | --- |
| Vraag | Geldt het op andere kaarten? | Is de vergelijking eerlijk op dezelfde kaart? |
| Seed 1 vs 77 | twee startwerelden | — |
| C0 vs C3 op seed 1 | — | zelfde W1, andere controller |
| Gelijk | regels, parameters | tick-0 staat |
| Verschillend | layout en toeval daarna | alleen de controller, daarna de geschiedenis |

Zonder clones vergelijk je controllers op verschillende borden.  
Zonder veel seeds generaliseer je vanaf één bord.

---

## 12. Benchmarks

Omdat inference lokaal kan (configureerbaar model, bijv. op een RTX 3090) zijn API-kosten geen harde limiet. Latency blijft de bottleneck: 10 organismen × N ticks = N×10 LLM-calls per run.

### Fast benchmark (iedere controller, veel seeds)

```text
ticks = 1000
```

### Evolution benchmark (C0–C2)

```text
ticks = 10_000   # later optioneel 100_000
```

### LLM long-run

Alleen nadat fast-benchmark iets interessants toont:

```text
ticks = 5_000 of 10_000
```

Seed-aantallen (in het manifest vastleggen):

```text
C0–C2:  100 seeds   (fast en/of evolution, naar draaitijd)
C3–C6:   20–50 seeds op fast; long-run minder
```

**100 seeds is het initiële benchmarkbudget, geen statistisch bewijs dat N=100 “voldoende” is.** De uiteindelijke sample size wordt beoordeeld aan de hand van effect-size-stabiliteit en betrouwbaarheidsintervalbreedte, nadat de eerste runs bestaan.

Eén officiële vergelijking tussen alle controllers gebruikt **dezelfde tick-count** (fast). Langere C0–C2-runs zijn extra, geen stille vervanging van de vergelijking.

---

## 13. Primaire experimentconfiguratie

Eerste officiële benchmark (iedere wijziging = nieuwe experimentversie):

```text
world:             32 × 32 torus
initial agents:    10
resource sites:    20
resource value:    30
regen_delay:       15
observation:       radius 2 (5×5 egocentrisch)
actions:           5
initial energy:    100
base_metabolism:   1
movement_cost:     1
reproduction:      threshold 150, cost 75, child 75
ticks (fast):      1000
ticks (evolution): 10000
```

---

## 14. Wetenschappelijke vergelijking

Niet: “welke is het slimst?”

Wel:

> **Welke kwalitatieve en kwantitatieve veranderingen ontstaan wanneer het decision mechanism wordt vervangen?**

```text
Random → Reactive → Evolutionary → LLM → LLM+Memory
                                      └→ + Evolution
```

Iedere inhoudelijke claim wordt tegen C0 (random-controller baseline) getoetst, over meerdere seeds, daarna tegen C1 en C2.

Omdat clones per seed dezelfde tick-0-wereld delen, is de primaire vergelijking **paired-by-seed**:

```text
Δ_i = metric(C2, seed_i) − metric(C0, seed_i)
```

Analyseer de distributie van Δ, niet alleen twee losse gemiddelden. Rapporteer per primaire metric minimaal: mediaan, mean, sd, betrouwbaarheidsinterval, effect size, en de per-seed-distributie. Zelfde voor C0 vs C1 en C1 vs C2.

Metrics worden gerapporteerd over de **hele run** en, waar relevant, over expliciet gedefinieerde tijdvensters (bijv. 0–100 vs 800–1000). **Geen steady-state-aanname** tenzij die getest is. `mean_age` alleen interpreteren samen met population size: lage mean age kan veel geboortes betekenen of juist snel sterven.

Ablations na de eerste resultaten, onder andere:

```text
C2 vs C0-R vs C0     # genetic evolution vs population dynamics vs baseline
C2 vs C2-oracle      # random-init evolution vs fixed cardinal phenotype (same 9 features)
C2-diag / denser features   # later, nieuwe experimentversie; niet v0.1-C2 herschrijven
C6
 ├── zonder memory   (= C5)
 ├── zonder evolution (= C4)
 └── zonder beide    (= C3)

C3 prompt A  vs  C3 prompt B
```

---

## 15. Configuratie

Geen experimentele parameters hardcoden. YAML (of equivalent) plus een experiment-manifest.

Voorbeeld:

```yaml
world:
  width: 32
  height: 32
  torus: true
  resource_count: 20
  resource_value: 30
  regen_delay: 15

population:
  initial_size: 10

simulation:
  ticks: 1000

organism:
  initial_energy: 100
  base_metabolism: 1
  movement_cost: 1
  reproduction_energy_threshold: 150
  reproduction_cost: 75

observation:
  radius: 2

controller:
  type: evolutionary   # random | reactive | evolutionary | llm | llm_memory | ...

llm:
  model: null          # configureerbaar, nooit hardcoded
  endpoint: null
  temperature: 0.0
  prompt_id: llm_a     # llm_a | llm_b | llm_a_memory | llm_b_memory
  prompt_version: 1

experiment:
  seed: 123456
  experiment_id: ...
```

---

## 16. Randomness

Drie gescheiden RNG-stromen. De renderer en analytics mogen ze **nooit** aanraken.

```text
world_rng         # initiële plaatsing van sites en organismen
evolution_rng     # initiële genomes, mutatie-draws
controller_rng    # C0-keuzes, C1-ties, C2-argmax-ties
```

Movement- en birth-conflicts gebruiken **geen** van deze stromen, maar de hash uit §4.8 / §4.9. Daardoor koppelt extra conflict in de ene clone niet de RNG-staat van de andere.

`controller_rng` is stateful binnen een run (zie §9.1). Dat is geen bug.

Iedere stroom wordt geïnitialiseerd uit de experiment-seed plus een vaste namespace:

```text
world_rng      ← seed_derived("world")
evolution_rng  ← seed_derived("evolution")
controller_rng ← seed_derived("controller")
```

Exacte `seed_derived` (bijv. `sha256(f"{seed}:{namespace}")` als int) vastleggen in code en tests.

Voor LLM: sampling hangt van het model/backend af. Temperature, backend, model hash, quantisatie en runtime loggen. Niet-determinisme expliciet als beperking in het manifest (§9.4).

---

## 17. Reproduceerbaarheid

Iedere run krijgt minimaal:

```text
experiment_id
run_id
seed
controller_type
controller_version
prompt_id
prompt_version
system_prompt_hash
world_version
config_version
git_commit          # verplicht
model_name          # of null
model_file_hash     # of null
quantization        # of null
inference_backend  # of null
cuda_version        # of null
runtime_version     # of null
model_parameters
ticks
timestamp
determinism_notes   # LLM: reproduktie alleen onder identieke stack; zie §9.4
```

Resultaten worden nooit overschreven.

Niet-LLM: dezelfde code + config + seed = exact dezelfde run.

---

## 18. Event logging

Geen informatie mag alleen in terminal output bestaan.

Niet loggen: `RESOURCE_DETECTED` (dat is perceptie, geen wereldmutatie).

### Iedere tick, per levend organisme

```text
OBSERVATION     # serialisatie van de 5×5 + energy + age
ACTION          # Decision.action (of fallback STAY)
MEMORY_WRITE    # indien niet None; pas zichtbaar T+1
```

### World events

```text
RESOURCE_CONSUMED
RESOURCE_REGEN
MOVE                # organism_id, from, to  — iedere geslaagde verplaatsing
MOVE_BLOCKED
MOVE_CONFLICT       # pretenders + winnaar; niet COLLISION
BIRTH
DEATH
ENERGY_CHANGED      # of afleidbaar uit de bovenstaande; als event mag, niet verplicht dubbel
INVALID_ACTION
TICK_STARTED
TICK_FINISHED
```

### LLM (per call)

Immutable raw trace:

```text
timestamp
tick
organism_id
observation
memory
genome
prompt
prompt_version
system_prompt_hash
model
model_config
raw_output          # ongewijzigd
parsed_action
self_reported_rationale   # of null
latency_ms
input_tokens
output_tokens
valid
fallback            # STAY of null
```

Replay en GIF komen uit events/snapshots, **niet** uit hersimuleren, tenzij een expliciete “resimulate” tool dat doet voor verificatie.

---

## 19. Snapshots en dataformaat

Periodieke snapshots, configureerbaar. Minimaal tick 0 en einde-run. Aanbevolen: 0, 100, 500, 1000, … (afhankelijk van tick-budget).

Een snapshot bevat:

```text
tick
world parameters
resource sites + of food aanwezig + last_consumed_tick
alle organismen (inclusief genome/memory indien aanwezig)
population
seed / experiment ids
```

```text
events.jsonl          # JSONL
snapshots             # JSON of compressed JSON
analyse               # CSV (Parquet optioneel later)
metadata              # JSON
```

Geen database in v0.1.

```text
experiments/
  configs/
  manifests/
  results/            # nooit overschrijven
```

---

## 20. Analytics

Analytics zit **niet** in de simulatie-engine. Zelfde Python-package mag, als aparte pipeline:

```text
simulation → raw events/snapshots → analytics → metrics → plots
```

Simulator schrijft alleen raw data. Metrics altijd offline herberekenbaar.

### v0.1 metrics (implementeren)

```text
population_size
birth_rate
death_rate
mean_age
time_to_extinction
mean_energy
energy_variance
total_energy
resources_consumed_count
action_distribution
action_entropy
invalid_action_rate
```

LLM extra: tokens, latency, cost-estimate (lokaal: 0 geld, wél tokens/tijd).

### Later berekenbaar, nu nog niet verplicht plotten

Raw data moet volstaan voor:

```text
clustering / nearest-neighbor / spatial entropy
lineages / genome diversity
behavioral diversity
memory writes/reads
interaction-achtige occupancy-patronen
```

Geen samengestelde “intelligence score”.

`mean_age` nooit als alleenstaande “fitness”-proxy gebruiken; altijd samen met `population_size` en birth/death.

### Statistische vergelijking (v0.1, geen zwaar framework)

Voor iedere primaire metric, per controller:

```text
median, mean, sd, confidence interval, per-seed distribution, effect size
```

Voor clones, paired:

```text
C0 vs C1
C0 vs C2
C1 vs C2
```

```text
Δ_i = metric(A, seed_i) − metric(B, seed_i)
```

Rapporteer de distributie van Δ. Dat is sterker dan twee ongepaarde gemiddelden.

Tijdvensters: hele run, plus optioneel expliciete windows. Geen steady-state tenzij getest.

---

## 20.1 Operational definition of emergence

In v0.1 wordt emergence **niet** als één scalar gedefinieerd.

> A behavior is a candidate emergent phenomenon when it is a persistent system-level pattern that is not explicitly encoded as a global rule in the controller or the environment, and that is reproducible across independent runs/seeds.

Pipeline:

```text
candidate emergence
        ↓
visual observation
        ↓
quantitative metric
        ↓
cross-seed replication
        ↓
ablation
```

**A visually interesting GIF is not evidence of emergence. It is a hypothesis-generating observation.**

Wat géén bewijs is: één run, één seed, één anekdotische clustering, een rationale-string van een LLM, of een patroon dat al in de controllerregel staat (bijv. C1 die naar food loopt).

---

## 21. Visualization en GIFs

Minimaal een rasterweergave: resources en organismen duidelijk, stabiele glyph per `organism_id` (niet alleen A–Z; bij >26 ids cijfers of kleur+label).

```text
Tick: 1024
Population: 8
```

Automatische export uit opgeslagen runs:

```text
C0_random_seed123.gif
C1_reactive_seed123.gif
C2_evolution_seed123.gif
...
comparison_seed123.gif
```

Comparison: condities synchroon naast elkaar, zelfde schaal, timestep, initiële staat, rendering, camera.

Renderer gebruikt geen experiment-RNGs.

Een visueel interessant GIF is geen bewijs van emergence. Zie §20.1.

---

## 22. Repository structure

```text
emergence-lab/
├── README.md
├── pyproject.toml
├── LICENSE
├── spec.md
│
├── src/emergence_lab/
│   ├── world/
│   │   ├── world.py
│   │   ├── organism.py
│   │   ├── resource.py
│   │   └── observation.py
│   ├── controllers/
│   │   ├── base.py
│   │   ├── random.py
│   │   ├── reactive.py
│   │   ├── evolutionary.py
│   │   ├── llm.py
│   │   └── verification.py
│   ├── llm/                   # prompts, parse, Ollama-client (stdlib urllib)
│   │   ├── prompts.py
│   │   ├── parse.py
│   │   └── ollama.py
│   ├── simulation/
│   │   ├── engine.py
│   │   ├── events.py
│   │   ├── snapshots.py
│   │   └── rng.py
│   ├── analytics/          # offline pipeline, geen world-mutations
│   │   ├── metrics.py
│   │   └── statistics.py
│   └── visualization/
│       ├── renderer.py
│       └── gif.py
│
├── experiments/
│   ├── configs/
│   ├── manifests/
│   └── results/
│
├── notebooks/
└── tests/
    ├── test_invariants.py
    └── test_verification_controllers.py
```

Python 3.11+. Deps: pytest, pyyaml, pillow (GIF). C3 praat met Ollama via **stdlib urllib**; geen extra LLM-package.

`README.md` moet minstens bevatten:

```text
Research question
Experimental matrix
What counts as evidence
What does NOT count as evidence
How to reproduce
```

Daarin expliciet:

> **A visually interesting GIF is not evidence of emergence. It is a hypothesis-generating observation.**

En: dit is een mechanistisch ALife-model, geen biologisch model.

---

## 23. Testvereisten

### World

- torus wrap
- één organisme per cel
- geen swap / geen enter-occupied
- conflict-hash identiek over herhaalde calls
- resource cooldown, inclusief exacte timing:

```text
consumed at tick T
regen_delay = 25
unavailable T+1 … T+24
available at T+25 iff cell free of organism and resource
```

- geen regen op bezette cel
- energy: STAY −1, MOVE −2, consume +30
- death bij energy <= 0
- initiële plaatsing: geen overlap, geen spawn-op-food
- newborn op resource: energy 75+resource_value, resource weg, `last_consumed_tick = tick`

### Simultaneïteit

- alle decisions van tick T gebruiken uitsluitend state T (geen organism ziet een al verplaatste buur van dezelfde tick)
- `memory_write` van tick T is niet zichtbaar in `decide` van tick T

### Reproduction

- 75/75 boekhouding
- geen geboorte zonder vrije 4-buur
- birth-conflict: één winnaar, verliezer houdt energy
- mutatie en inheritance
- `child.controller_condition == parent.controller_condition`

### Invarianten (iedere tick, model verification)

```text
number_of_occupied_organism_cells == number_of_alive_organisms
no dead organism participates in observation, energy, movement, or reproduction
resource_consumed ⇒ resource was present
resource_regen ⇒ site cooldown satisfied and cell free
total living + dead_this_run accounting:
    living == founders + births - deaths
```

### Verification controllers (niet in de experimentele matrix)

Alleen engine-validatie:

```text
AlwaysStayController
AlwaysNorthController
```

Sanity: AlwaysStay op een patch zonder regen-onder-organisme sterft volgens het energiebudget; AlwaysNorth wrapt op de torus zonder randartefact. Niet als wetenschappelijke conditie rapporteren.

### Controllers

- C0/C1/C2 geven een `Decision` met een actie uit de action space
- engine accepteert invalid en valt terug op STAY
- C3: parse NORTH/SOUTH/EAST/WEST/STAY; garbage → STAY + `INVALID_ACTION`; raw output in `LLM_CALL`
- C3 tests gebruiken een fake client (geen netwerk)
- C4: parse `MEMORY:`; write T zichtbaar T+1; FIFO/cap; te lange string afkappen; invalid mag nog schrijven

### Reproducibility

- identieke seed + C0/C1/C2 ⇒ identieke event-log (hash van jsonl)

### Logging / replay / GIF

- iedere world mutation heeft een event, inclusief geslaagde `MOVE`
- replay zonder hersimuleren
- GIF uit opgeslagen run

---

## 24. Wat NIET in v0.1 hoort

Niet implementeren:

- communicatie, taal, trading, combat, buildings, societies
- explicit goals in de **wereld** (LLM-prompt B is een aparte ablation)
- planning systems, reflection, tool use, internet
- multi-agent orchestration, distributed execution
- reinforcement learning / C7
- automatic prompt evolution
- vector memory / RAG
- inference cache als stille optimalisatie
- energy of organism_id als collision-priority
- live-random resource spawn op willekeurige lege cellen
- globale coördinaten of IDs in de observation
- `EAT` als actie
- complexe physics
- C3-R / C4-R in Milestone 1
- energy als extra C2-feature
- scalar “emergence score”

Die kunnen later afzonderlijke experimenten of ablations worden.

---

## 25. Ontwerpprincipe

**Minimalism over features.**

Bij interessant gedrag:

1. reproduceer het
2. meet het
3. meerdere seeds
4. vergelijk met C0 (en C1/C2)
5. ablations
6. probeer het systeem kleiner te maken

Doel:

> **De minimale wereld en minimale regels vinden die het waargenomen gedrag nog steeds produceren.**

---

## 26. Definition of Done

### Milestone 1

- [ ] één wereld reproduceerbaar draait (torus, patches, simultane ticks)
- [ ] collisions via hash, niet via ID/energy
- [ ] C0, C1, C2 op dezelfde `Decision`-interface
- [ ] same-world clones vanaf tick-0 snapshot
- [ ] events + snapshots + manifests, inclusief `MOVE` en `MOVE_CONFLICT`
- [ ] replay zonder hersimuleren
- [ ] GIF-export + comparison-GIF
- [ ] seed-reproducibility voor C0–C2
- [ ] analytics offline, paired-by-seed Δ
- [ ] tests uit §23 groen (invarianten + AlwaysStay/AlwaysNorth)
- [ ] newborn consume-pad getest
- [ ] fast benchmark (1000 ticks) en evolution benchmark (10000 ticks) automatisch over meerdere seeds voor C0–C2

### Milestone 2

- [x] C3 met configureerbaar model en prompt A
- [x] prompt B als ablation
- [x] volledige LLM decision traces (`LLM_CALL`)
- [x] C4 memory (list[str], cap 20); write pas zichtbaar op T+1
- [x] `Decision.memory_write` / `rationale` (C4 write-pad in LlmController + engine)
- [x] invalid LLM output → STAY
- [ ] LLM traces inclusief model hash, backend, quantisatie (backend=ollama, hash/quant null tot `ollama show`)
- [ ] fast benchmark voor C3/C4

### Milestone 3

- [ ] C5 en C6
- [ ] automatische vergelijking tussen controllers op clones + seeds

---

## 27. Implementatievolgorde

**Begin niet met de LLM.**

```text
1.  World + torus + occupancy
2.  Organism
3.  Resource patches + regen
4.  Observation (5×5 egocentrisch)
5.  Action + validatie
6.  Simulation engine (pipeline §4.5)
7.  Collision hash
8.  Energy + death
9.  Event logging + snapshots
10. RNG-namespaces
11. Replay
12. Renderer / GIF
13. C0 Random
14. C1 Reactive
15. AlwaysStay / AlwaysNorth (tests)
16. Reproduction
17. C2 Evolutionary
18. Analytics (v0.1 metrics + paired Δ)
19. Experiment runner (seeds × clones)
20. C3 LLM
21. C4 Memory
22. C5 / C6
```

Na stap 19 is Milestone 1 klaar.

---

## 28. Kernhypothese

> **Kan globale complexiteit ontstaan uit zeer eenvoudige lokale regels, en hoe verandert die emergente dynamiek wanneer het lokale decision mechanism wordt vervangen door evolutie, pretrained computation en individuele memory?**

---

## 29. Roadmap na v0.1 (niet implementeren nu)

```text
Milestone 4    Online learning (C7, C8)
Phase 5        Individuality — identieke start, verschillende ervaringen, stabiele profielen?
Phase 6        Self-model — informatie over zichzelf die latere beslissingen stuurt?
Phase 7        Social emergence — recognition, interaction, communication, groups
```

Optionele wereld-ablation later: `conflict_resolution: random_hash | energy | organism_id` om te meten of contest competition het signaal overstemt. Default in v0.1 blijft `random_hash`.

---

**Einde spec v0.2 (frozen).** Implementeer Milestone 1 tegen dit document. Geen extra features, geen rijker genome, geen social, geen RL, geen verdere spec-theorie tot de eerste werelden draaien. Wijzigingen aan wereldregels of defaults = nieuwe spec-versie en nieuwe experimentversie.
