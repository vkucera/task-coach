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
#import "i18n.h"

@implementation TaskCelliPad

@synthesize subject;
@synthesize priority;
@synthesize infos;
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
	[ID release];

	self.subject = nil;
	self.priority = nil;
	self.infos = nil;
	self.description = nil;
	self.tracking = nil;
	self.check = nil;

	[super dealloc];
}

- (NSManagedObjectID *)ID
{
	return ID;
}

- (void)setTask:(CDTask *)task target:(id)theTarget action:(SEL)theAction
{
	[ID release];
	ID = [[task objectID] retain];
	
	target = theTarget;
	action = theAction;

	subject.text = task.name;

	if ([task.longDescription length])
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
	infos.text = [@", " stringByJoiningStrings:cats];
	[cats release];
	
	NSInteger prio = [task.priority intValue];

	priority.text = [NSString stringWithFormat:@"%d", prio];
	priority.textColor = [UIColor colorWithRed:(int)(255.0 * prio / 15) green:(int)(255 - 255.0 * prio / 15) blue:0 alpha:1.0];

	UIColor *textColor = nil;

	switch ([[task dateStatus] intValue])
	{
		case TASKSTATUS_COMPLETED:
			textColor = [UIColor greenColor];
			break;
		case TASKSTATUS_OVERDUE:
			textColor = [UIColor redColor];
			break;
		case TASKSTATUS_DUESOON:
			textColor = [UIColor orangeColor];
			break;
		case TASKSTATUS_STARTED:
			textColor = [UIColor blueColor];
			break;
		case TASKSTATUS_NOTSTARTED:
			textColor = [UIColor grayColor];
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
}

- (void)onTapImage
{
	[target performSelector:action withObject:self];
}

- (void)drawRect:(CGRect)rect
{
	CGContextRef context = UIGraphicsGetCurrentContext();
	CGContextDrawTiledImage(context, CGRectMake(0, 0, 30, 30), bgImage.CGImage);
	
	[super drawRect:rect];

	CGContextSaveGState(context);
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
