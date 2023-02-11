import pandas as pd

HANGING_MAN_BODY = 15.0
HANGING_MAN_HEIGHT = 75.0
SHOOTING_STAR_HEIGHT = 25.0
SPINNING_TOP_MIN = 40
SPINNING_TOP_MAX = 60
MARUBOZU = 98.0
ENGULFING_FACTOR = 1.1
TWEEZER_BODY = 15.0
TWEEZER_HL = 0.01
TWEEZER_TOP_BODY = 40.0
TWEEZER_BOTTOM_BODY = 60.0
MORNING_STAR_PREV2_BODY = 90.0
MORNING_STAR_PREV_BODY = 10.0

def apply_hanging_man(row):
    if row.body_bottom_perc > HANGING_MAN_HEIGHT:
        if row.body_perc <HANGING_MAN_BODY:
            return True
    return False  
    
def apply_shooting_star(row):
    if row.body_bottom_perc < SHOOTING_STAR_HEIGHT:
        if row.body_perc <HANGING_MAN_BODY:
            return True
    return False  
    
def apply_spinning_top(row):
    if row.body_bottom_perc < SPINNING_TOP_MAX:
        if row.body_bottom_perc > SPINNING_TOP_MIN:
            return True
    return False  
    
apply_marubozu = lambda x:x.body_perc>MARUBOZU

def apply_engulfing(row):
    if row.direction !=row.direction_prev:
        if row.body_size > row.body_size_prev * ENGULFING_FACTOR:
            return True
    return False
    


def apply_tweezer_top(row):
    if abs(row.body_size_change)<TWEEZER_BODY:
        if row.direction == -1 and row.direction!=row.direction_prev:
            if abs(row.low_change)<TWEEZER_HL and abs(row.high_change)<TWEEZER_HL:
                if row.body_top_perc<TWEEZER_TOP_BODY:
                    return True
    return False
    
def apply_tweezer_bottom(row):
    if abs(row.body_size_change)<TWEEZER_BODY:
        if row.direction == 1 and row.direction!=row.direction_prev:
            if abs(row.low_change)<TWEEZER_HL and abs(row.high_change)<TWEEZER_HL:
                if row.body_bottom_perc>TWEEZER_BOTTOM_BODY:
                    return True
    return False


def apply_morning_star(row,direction=1):
    if row.body_perc_prev_2>MORNING_STAR_PREV2_BODY:
        if row.body_perc_prev<MORNING_STAR_PREV_BODY:
            if row.direction==direction and row.direction_prev_2 != direction:
                if direction==1:
                    if row.mid_c > row.mid_point_prev_2:
                        return True
                else:
                    if row.mid_c < row.mid_point_prev_2:
                        return True
                        
    return False  

def apply_candle_props(df: pd.DataFrame):
    direction = df.mid_c - df.mid_o
    df['body_size'] = abs(direction)
    df['direction'] = [1 if x>=0 else -1 for x in direction]
    full_range = df.mid_h - df.mid_l
    df['body_perc'] = (df['body_size']/full_range) * 100
    df['body_lower'] = df[['mid_c','mid_o']].min(axis=1)
    df['body_upper'] = df[['mid_c','mid_o']].max(axis=1)
    df['body_bottom_perc'] = (df.body_lower - df.mid_l)/full_range * 100
    df['body_top_perc'] = (df.mid_h - df.body_upper)/full_range * 100
    df['low_change'] = df.mid_l.pct_change()
    df['high_change'] = df.mid_h.pct_change()
    df['body_size_change']= df.body_size.pct_change()

    df['mid_point']= full_range/2+df.mid_l
    df['mid_point_prev_2']= df['mid_point'].shift(2)
    df['body_size_prev'] = df.body_size.shift(1)
    df['direction_prev'] = df.direction.shift(1)
    df['direction_prev_2'] = df.direction.shift(2)
    df['body_perc_prev'] = df.body_perc.shift(2)
    df['body_perc_prev_2'] = df.body_perc.shift(2)
    return df

def set_candle_patterns(df_an: pd.DataFrame):
    df_an['HANGING_MAN'] = df_an.apply(apply_hanging_man, axis =1)
    df_an['SHOOTING_STAR'] = df_an.apply(apply_shooting_star, axis =1)
    df_an['SPINNING_TOP'] = df_an.apply(apply_spinning_top, axis =1)
    df_an['MARUBOZU'] = df_an.apply(apply_marubozu, axis =1)
    df_an['ENGULFING'] = df_an.apply(apply_engulfing, axis =1)
    df_an['TWEEZER_TOP'] = df_an.apply(apply_tweezer_top, axis =1)
    df_an['TWEEZER_BOTTOM'] = df_an.apply(apply_tweezer_bottom, axis =1)
    df_an['MORNING_STAR'] = df_an.apply(apply_morning_star, axis =1)
    df_an['EVENING_STAR'] = df_an.apply(apply_morning_star, axis =1,direction=-1)

def apply_patterns(df: pd.DataFrame):
    df_an = apply_candle_props(df)
    set_candle_patterns(df_an)
    return df


