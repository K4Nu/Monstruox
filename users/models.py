from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.models import User
import math
from django.utils import timezone

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    nickname=models.CharField(max_length=50,
                              unique=True,
                              validators=[
                                  MinLengthValidator(3),
                                  RegexValidator(
                                      regex="^[a-zA-Z0-9_]*$",
                                      message='Nickname can only contain letters, numbers, and underscores'
                                  )
                              ])
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True,null=True)
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    coins = models.PositiveIntegerField(default=100)
    energy = models.PositiveIntegerField(default=100)
    max_energy = models.PositiveIntegerField(default=100)

    """
    Battle Statistics 
    """
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    best_streak = models.PositiveIntegerField(default=0)

    """
    Achievements
    """
    battles_fought = models.PositiveIntegerField(default=0)
    creatures_caught = models.PositiveIntegerField(default=0)
    items_collected = models.PositiveIntegerField(default=0)
    quests_completed = models.PositiveIntegerField(default=0)

    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_energy_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["level", "xp"], name="profile_level_xp_idx"),
            models.Index(fields=["wins", "losses"], name="profile_wins_losses_idx"),
        ]

    def __str__(self):
        return f'{self.nickname} {self.level}Lvl'

    @property
    def total_games(self):
        return self.wins + self.losses

    @property
    def win_ratio(self):
        if self.total_games > 0:
            return round((self.wins / self.total_games) * 100, 2)
        return 0

    def calculate_xp_for_next_level(self):
        """Calculate XP needed for next level using a common game progression formula"""
        return int(100 * (math.pow(1.35, self.level)))

    def add_xp(self,amount):
        """Handle level up mechanics"""
        self.xp += amount
        while self.xp > self.calculate_xp_for_next_level():
            self.level_up()

    def level_up(self):
        """Handle level up mechanics"""
        self.level+=1
        self.max_energy = int(100+1.45*self.level)
        self.energy=self.max_energy
        self.xp-=self.calculate_xp_for_next_level()

    def record_battle(self, won, xp_gained, coins_gained):
        """Record battle results and update stats"""
        self.battles_fought += 1
        if won:
            self.wins += 1
        else:
            self.losses += 1
        self.update_streak(won)
        self.add_xp(xp_gained)
        self.coins += coins_gained
        self.save()

    def spend_energy(self,amount):
        if self.energy >=amount:
            self.energy-=amount
            self.save()
            return True
        return False

    def regenerate_energy(self):
        """Regenerate energy based on time passed"""
        minutes_passed=(timezone.now()-self.last_energy_update).total_seconds()/60
        energy_to_add=int(minutes_passed/5)
        if energy_to_add > 0:
            self.energy=min(self.max_energy, self.energy + energy_to_add)
            self.last_energy_update=timezone.now()
            self.save()

    def can_receive_daily_reward(self):
        """Check if user can receive daily reward"""
        now = timezone.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return self.last_login < midnight

    def update_streak(self, won):
        """Update winning/losing streak"""
        if won:
            self.current_streak = max(1, self.current_streak + 1)
        else:
            self.current_streak = min(-1, self.current_streak - 1)
        self.best_streak = max(self.best_streak, abs(self.current_streak))

    def get_stats_summary(self):
        """Return a dictionary of key player statistics"""
        return {
            'level': self.level,
            'xp_to_next_level': self.calculate_xp_for_next_level() - self.xp,
            'win_ratio': self.win_ratio,
            'total_games': self.total_games,
            'best_streak': self.best_streak,
            'current_streak': self.current_streak,
            'rank': self.get_rank()
        }

class Friendship(models.Model):
    from_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="friends")
    to_user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="receiver")
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

        
