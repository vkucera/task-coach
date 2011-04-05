//
//  CDTask+Addons.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "CDTask.h"

#define TASKSTATUS_UNDEFINED         0
#define TASKSTATUS_TRACKING          1
#define TASKSTATUS_OVERDUE           2
#define TASKSTATUS_DUESOON           3
#define TASKSTATUS_STARTED           4
#define TASKSTATUS_NOTSTARTED        5
#define TASKSTATUS_COMPLETED         6

#define REC_DAILY   0
#define REC_WEEKLY  1
#define REC_MONTHLY 2
#define REC_YEARLY  3

@interface CDTask (Addons)

- (void)computeDateStatus;
- (CDEffort *)currentEffort;

- (void)toggleCompletion;

// For recurrent tasks
- (NSDate *)computeNextDate:(NSDate *)date;

// This does not save the changes
- (void)startTracking;
- (void)stopTracking;

@end
