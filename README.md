# NGL Flash Separator Calculator
## What is this
A python script that models a single-stage flash separator for a natural gas liquids mixture (methane, ethane, propane, and n-butane). Give it temperature and pressure and it works out what fraction of the feed splits into vapor versus liquid and what each phase is made of, using Raoult's Law and the Rachford-Rice equation.

I built this while preparing for my MSc at University of Surrey, as a second project alongside my MEA CO2 capture calculator. Flash separators are everywhere in gas processing, and I wanted something more hands-on than just reading about VLE theory. 

## How the process works
Picture a high-pressure pipeline carrying liquid NGLs through a valve into a big empty drum. The instant the pressure drops across the valve, some of the mixture flashes into vapor right there - mostly methane, since it barely wants to be liquid in the first place. The vessel doesn't do any separating chemistry itself; it just gives the gas time to rise off the liquid before both streams leave through separate outlets.

The script follows this logic in order:
1. Calculate each component's vapor pressure at given temperature using the Antoine equation
2. Get K-values from Raoult's Law (K = vapor pressure / total pressure). This tells you how much each component "prefers" vapor over liquid
3. Solve the Rachford-Rice equation for the overall vapor fraction V, using SciPy's ```brentq``` root-finder
4. Work out liquid and vapor compositions from V and K-values
5. Check whether the chosen temperature and pressure are actually inside the two-phase region before running any of this. If they're not, the script tells you rather than crashing

## Results
Using -30°C and 5 bar as the operating conditions for a feed of 40% methane, 25% ethane, 20% propane, 15% n-butane:
- Vapor fraction: 0.7418 so about 74% of the feed vaporizes
- Vapor composition: mostly methane (0.5329) and ethane (0.3011)
- Liquid composition: mostly n-butane (0.4951) and propane (0.3835)

Makes sense physically. Methane's K-value is enormous at these conditions, so it ends up almost entirely in the vapor stream even though it's a minority of the feed by mole fraction. 

I also plotted a phase envelope which is a bubble point and dew point pressure across a range of temperatures, with my chosen operating point marked on it. It's a simplified version of the "PT envelope" utility in Aspen Plus or HYSYS: a map of where two-phase behaviour is even possible before you try running a flash calculation there.

<img width="1600" height="1200" alt="Bubble_Dew_Point_Curves" src="https://github.com/user-attachments/assets/bbe1e652-06e9-4fcb-9161-163b1de1b3d0" />

<img width="1600" height="1200" alt="Flash_Composition_Comparison" src="https://github.com/user-attachments/assets/17f623b2-46e4-4ada-aba1-0549011e6799" />

My first attempt at picking operating conditions was 60°C and 10 bar. The solver crashed immediately because ```f(a) and f(b) must have different signs```. Turned out the mixture was fully vapor at those conditions, so there was no flash to solve for. That's what led to building the two-phase check in the first place, rather than wrapping the crash in a try/except and calling it done. 

## Simplifications and assumptions I made 
This uses Raoult's Law, which assumes ideal mixture so there is no molecular interactions beyond what pure-component vapor pressure already accounts for. That's a reasonable approximation for a mixture of similar light hydrocarbons like this one, but it's still an approximation. Specifically: 
- No convergence to critical point. Real phase envelopes have the bubble and dew curves meeting at a single point at high pressure/temperature. Mine don't, since Raoult's Law doesn't produce that behaviour.
- Antoine constants only hold over the temperature range they were fitted for. Push far enough outside it and the vapor pressures stop meaning anything.
- No non-hydrocarbon components. Real NGL streams often carry CO2, H2S, nitrogen or water, which don't behave ideally alongside hydrocarbons.
- No pressure drop, no heat integration, no equipment sizing. This is a thermodynamic calculation, not a separator design.

A real design would use a cubic equation of state such as Peng-Robinson or Soave-Redlich-Kwong which handles non-ideal interactions between molecules properly. That's the default in Aspen Plus and HYSYS, and what I'll be using once I get to my dissertation modelling.

## How to run it
Needs Python 3, SciPy, and matplotlib:

```pip install -r requirements.txt```

Run the script. It prints the flash results to the terminal and saves two PNG charts to the same folder.

## What's next
Second independent project, alongside the MEA calculator. Between the two I've now covered mass/energy balance work and phase equilibrium which are both things I'll be using properly once I get into Aspen Plus for my dissertation. 



