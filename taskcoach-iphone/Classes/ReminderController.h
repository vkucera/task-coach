//
//  ReminderController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 06/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface ReminderController : NSObject
{
}

+ (ReminderController *)instance;

- (void)check:(BOOL)silent;

- (void)scheduleLocalNotifications;
- (void)unscheduleLocalNotifications;

@end
