//
//  CalendarTaskView.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "CalendarTaskView.h"

#import "DateUtils.h"

#import "CDTask.h"
#import "CDTask+Addons.h"

@implementation CalendarTaskView

@synthesize task;

- initWithTask:(CDTask *)theTask
{
	if ((self = [super initWithFrame:CGRectZero]))
	{
		task = [theTask retain];

		switch ([task.dateStatus intValue])
		{
			case TASKSTATUS_COMPLETED:
				self.backgroundColor = [UIColor greenColor];
				break;
			case TASKSTATUS_OVERDUE:
				self.backgroundColor = [UIColor redColor];
				break;
			case TASKSTATUS_DUESOON:
				self.backgroundColor = [UIColor orangeColor];
				break;
			case TASKSTATUS_STARTED:
				self.backgroundColor = [UIColor blueColor];
				break;
			case TASKSTATUS_NOTSTARTED:
				self.backgroundColor = [UIColor grayColor];
				break;
			default:
				break;
		}
	}
	
	return self;
}

- (NSString *)title
{
	return task.name;
}

- (NSString *)location
{
	return task.longDescription;
}

- (NSDate *)startDate
{
	return task.startDate;
}

- (NSDate *)endDate
{
	return task.dueDate;
}

- (void)drawRect:(CGRect)rect
{
	[super drawRect:rect];

	if ([[task children] count])
	{
		CGContextRef context = UIGraphicsGetCurrentContext();
		CGContextSaveGState(context);

		CGRect imgRect = rect;
		imgRect.origin.x = imgRect.origin.x + imgRect.size.width - 36;
		imgRect.origin.y = imgRect.origin.y + imgRect.size.height - 36;
		imgRect.size.width = 31;
		imgRect.size.height = 31;
		
		UIImage *img = [UIImage imageNamed:@"disclosure.png"];
		
		CGContextDrawImage(context, imgRect, img.CGImage);

		CGContextRestoreGState(context);
	}
}

@end
