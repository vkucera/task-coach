//
//  NSDate+Utils.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 09/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface NSDate (Utils)

// Current date, rounded to the minute start
+ (NSDate *)dateRounded;

// Midnight, today
+ (NSDate *)midnightToday;

@end
