//
//  TaskCelliPad.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCelliPad.h"
#import "CDTask.h"
#import "CDTask+Addons.h"
#import "CDCategory.h"
#import "String+Utils.h"
#import "CheckView.h"
#import "Configuration.h"
#import "DateUtils.h"
#import "i18n.h"

@implementation TaskCelliPad

@synthesize task;

@synthesize subject;
@synthesize priority;
@synthesize categoryInfos;
@synthesize description;
@synthesize tracking;
@synthesize check;

- initWithCoder:(NSCoder *)coder
{
	if ((self = [super initWithCoder:coder]))
	{
		bgImage = [[UIImage imageNamed:@"paper.png"] retain];
	}

	return self;
}

- (void)dealloc
{
	[bgImage release];
	[task release];

	self.subject = nil;
	self.priority = nil;
	self.categoryInfos = nil;
	self.description = nil;
	self.tracking = nil;
	self.check = nil;

    [dateInfos release];
	[super dealloc];
}

- (void)setTask:(CDTask *)theTask target:(id)theTarget action:(SEL)theAction
{
	self.task = theTask;
	
	target = theTarget;
	action = theAction;

	subject.text = task.name;

	if ([task.longDescription length] && ![Configuration configuration].compactTasks)
	{
		description.text = task.longDescription;
		description.hidden = NO;
		description.font = [UIFont fontWithName:@"MarkerFelt-Thin" size:17];
	}
	else
	{
		description.text = @"";
		description.hidden = YES;
	}

	NSMutableArray *cats = [[NSMutableArray alloc] init];
	for (CDCategory *cat in task.categories)
		[cats addObject:cat.name];
	categoryInfos.text = [@", " stringByJoiningStrings:cats];
	[cats release];
	
	NSInteger prio = [task.priority intValue];

	priority.text = [NSString stringWithFormat:@"%d", prio];
	priority.textColor = [UIColor colorWithRed:1.0 * prio / 15 green:1.0 - 1.0 * prio / 15 blue:0 alpha:1.0];

	UIColor *textColor = nil;
    dateInfos.text = @"";

	switch ([[task dateStatus] intValue])
	{
		case TASKSTATUS_COMPLETED:
			textColor = [UIColor greenColor];
            dateInfos.text = [NSString stringWithFormat:_("Completed %@"), [[UserTimeUtils instance] stringFromDate:task.completionDate]];
			break;
		case TASKSTATUS_OVERDUE:
			textColor = [UIColor redColor];
			dateInfos.text = [NSString stringWithFormat:_("Due %@"), [[UserTimeUtils instance] stringFromDate:task.dueDate]];
			break;
		case TASKSTATUS_DUESOON:
			textColor = [UIColor orangeColor];
			dateInfos.text = [NSString stringWithFormat:_("Due %@"), [[UserTimeUtils instance] stringFromDate:task.dueDate]];
			break;
		case TASKSTATUS_STARTED:
			textColor = [UIColor blueColor];
			if (task.dueDate)
				dateInfos.text = [NSString stringWithFormat:_("Due %@"), [[UserTimeUtils instance] stringFromDate:task.dueDate]];
			break;
		case TASKSTATUS_NOTSTARTED:
			textColor = [UIColor grayColor];
			if (task.startDate)
				dateInfos.text = [NSString stringWithFormat:_("Start %@"), [[UserTimeUtils instance] stringFromDate:task.startDate]];
			break;
		default:
			break;
	}

	subject.textColor = textColor;

	if ([task currentEffort])
	{
		tracking.image = [UIImage imageNamed:@"ledclock.png"];
	}
	else
	{
		tracking.image = nil;
	}

	if (task.completionDate)
	{
		check.image = [UIImage imageNamed:@"checked.png"];
	}
	else
	{
		check.image = [UIImage imageNamed:@"unchecked.png"];
	}

	[check setTarget:self action:@selector(onTapImage)];

	if ([task.children count])
		self.accessoryType = UITableViewCellAccessoryDetailDisclosureButton;
	else
		self.accessoryType = UITableViewCellAccessoryNone;
}

- (void)onTapImage
{
	[target performSelector:action withObject:self];
}

- (void)drawRect:(CGRect)rect
{
	CGContextRef context = UIGraphicsGetCurrentContext();
	CGContextSaveGState(context);
	CGContextClipToRect(context, rect);
	CGContextDrawTiledImage(context, CGRectMake(0, 0, 30, 30), bgImage.CGImage);
	CGContextRestoreGState(context);
	
	[super drawRect:rect];

	CGContextSaveGState(context);
	CGContextClipToRect(context, rect);
	CGContextSetRGBStrokeColor(context, 0, 0, 0, 1);
	CGFloat sizes[2] = { 2.0, 2.0 };
	CGContextSetLineDash(context, 0, sizes, 2);
	CGContextSetLineWidth(context, 1);
	CGContextMoveToPoint(context, 0, self.bounds.size.height - 1);
	CGContextAddLineToPoint(context, self.bounds.size.width, self.bounds.size.height - 1);
	CGContextStrokePath(context);
	CGContextRestoreGState(context);
}

@end
