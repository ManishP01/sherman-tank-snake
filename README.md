# Sherman Tank Snake 🚗💥

A unique hybrid game combining the legendary M4 Sherman tank combat mechanics with snake-style gameplay and strategic trap systems. Command your Sherman tank through enemy territory, leaving tactical trails and deploying explosive traps!

![Game Screenshot](screenshot.png)

## 🎮 Game Overview

Sherman Tank Snake is an innovative arcade-style game where you command a legendary M4 Sherman tank that leaves a tactical snake-like trail behind it. Use this trail strategically to trap enemies and create explosive traps while engaging in direct combat with your Sherman's 75mm cannon. Honor the legacy of one of WWII's most iconic tanks!

## ✨ Key Features

### 🚗 Authentic Sherman Tank Graphics
- **Detailed Sherman Design**: WWII-era M4 Sherman with rotating turret and 75mm cannon
- **Tank Treads**: Animated track segments representing Sherman's reliable drive system
- **Battle Damage Effects**: Progressive damage with smoke effects and weathering
- **Historical Accuracy**: Tank-style rotation and movement true to Sherman mechanics

### 🐍 Enhanced Snake Trail System
- **Extended Visibility**: Trail segments last 2+ seconds for better strategic planning
- **Fading Effects**: Smooth alpha blending as segments disappear
- **Blinking Warning**: Trail blinks rapidly before disappearing
- **Trap Visualization**: Active traps show pulsing red connections

### 💥 Strategic Combat System
- **Dual Weapon Types**:
  - **Direct Fire**: Space bar to fire 75mm Sherman cannon rounds
  - **Trap System**: T key to activate explosive trail traps
- **Progressive Damage**: Tank takes damage instead of instant death
- **Capability Loss**: Damaged tanks move and rotate slower
- **Risk vs Reward**: Own trap explosions can damage your tank

### 🎯 Enemy Types
- **Basic Enemies** (Red circles): Standard movement, 20 points
- **Fast Enemies** (Orange triangles): Erratic movement, 30 points  
- **Tank Enemies** (Brown squares): Heavy armor, seeks player, 50 points

### 🏆 Game Progression
- **Wave System**: Increasing difficulty with new enemy types
- **Score Multipliers**: Trap kills award double points
- **Dynamic Spawning**: Enemy spawn rate increases each wave

## 🎮 Controls

| Key | Action |
|-----|--------|
| **WASD** / **Arrow Keys** | Move and rotate Sherman tank |
| **Space** | Fire 75mm cannon |
| **T** | Activate trap (requires 4+ trail segments) |
| **R** | Restart game (when game over) |
| **ESC** | Quit game |

## 🎯 Gameplay Strategy

### Basic Strategy
1. **Movement**: Use tank-style controls to navigate and position
2. **Trail Building**: Move continuously to build your snake trail
3. **Enemy Engagement**: Choose between direct fire or trap tactics

### Advanced Tactics
1. **Encirclement**: Surround groups of enemies with your trail
2. **Trap Timing**: Activate traps when enemies are inside your trail
3. **Positioning**: Stay away from your own trap blast radius
4. **Damage Management**: Avoid taking damage to maintain full capabilities

### Trap System
- **Setup**: Create a closed loop with your trail around enemies
- **Activation**: Press T to arm the trap (5-second timer)
- **Execution**: Trapped enemies panic and move frantically
- **Explosion**: Massive blast destroys all trapped enemies
- **Caution**: Stay clear of blast radius to avoid self-damage

## 🛠️ Technical Requirements

### Dependencies
```bash
pip install pygame
```

### System Requirements
- Python 3.7+
- Pygame 2.0+
- 800x600 display resolution minimum

## 🚀 Installation & Running

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/sherman-tank-snake.git
   cd sherman-tank-snake
   ```

2. **Install dependencies**:
   ```bash
   pip install pygame
   ```

3. **Run the game**:
   ```bash
   python sherman_tank_snake.py
   ```

## 🎨 Game Mechanics

### Tank Damage System
- **Healthy**: Full speed and rotation (Green tank)
- **Damaged**: 40% speed reduction, 30% rotation penalty (Yellow tank)
- **Critical**: 80% speed reduction, 60% rotation penalty (Brown tank)
- **Destroyed**: Game over

### Scoring System
- **Food Collection**: 10 points
- **Direct Kills**: 20-50 points based on enemy type
- **Trap Kills**: Double points (40-100 points)
- **Wave Progression**: Every 300 points advances to next wave

### Trail Mechanics
- **Segment Lifetime**: 120+ frames (2+ seconds)
- **Visibility**: Gradual fading with alpha blending
- **Collision**: Only visible segments can trap enemies
- **Trap Activation**: Requires minimum 4 segments in closed loop

## 🎮 Game States

### Playing
- Tank movement and combat
- Enemy AI and spawning
- Trail management and trapping
- Score tracking and wave progression

### Game Over
- Triggered when tank takes maximum damage
- Display final score and wave reached
- Option to restart with R key

## 🔧 Code Structure

```
sherman_tank_snake.py
├── TankSnake class      # M4 Sherman tank with authentic WWII graphics
├── Enemy class          # Axis forces with different combat behaviors  
├── Bullet class         # 75mm cannon projectile system
├── Food class           # Supply drops and ammunition
├── Explosion class      # Visual effects for tactical explosions
└── main()              # Combat simulation and event handling
```

## 🎯 Future Enhancements

- [ ] Sound effects and background music
- [ ] Power-ups and special weapons
- [ ] Multiplayer support
- [ ] Level editor
- [ ] Achievement system
- [ ] Leaderboard integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python and Pygame
- Inspired by classic Snake and Tank games
- Enhanced with modern game design principles

## 📞 Contact

- **Developer**: [Your Name]
- **Email**: [your.email@example.com]
- **GitHub**: [@yourusername](https://github.com/yourusername)

---

**Command your Sherman tank through enemy territory! 🚗💥**
