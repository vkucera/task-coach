//
//  CalendarTaskView.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "ODCalendarDayEventView.h"

@class CDTask;

@interface CalendarTaskView : ODCalendarDayEventView
{
	CDTask *task;
}

@property (nonatomic, readonly) CDTask *task;

- initWithTask:(CDTask *)task;

@end
