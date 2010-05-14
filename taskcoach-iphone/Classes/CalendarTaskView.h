//
//  CalendarTaskView.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <TapkuLibrary/ODCalendarDayEventView.h>

@class Task;

@interface CalendarTaskView : ODCalendarDayEventView
{
	Task *task;
}

@property (nonatomic, readonly) Task *task;

- initWithTask:(Task *)task;

@end
