//
//  TaskCellBig.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 22/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "Task.h"
#import "TaskCellBig.h"
#import "Database.h"
#import "Statement.h"
#import "String+Utils.h"
#import "i18n.h"

@implementation TaskCellBig

@synthesize infosLabel;
@synthesize categoriesLabel;

- (NSString *)trackingLedName
{
	return @"ledclockbig.png";
}

- (NSString *)completedLedName
{
	return @"ledgreenbig.png";
}

- (NSString *)overdueLedName
{
	return @"ledredbig.png";
}

- (NSString *)dueSoonLedName
{
	return @"ledorangebig.png";
}

- (NSString *)startedLedName
{
	return @"ledbluebig.png";
}

- (NSString *)notStartedLedName
{
	return @"ledgreybig.png";
}

- (void)dealloc
{
	[infosLabel release];
	[categoriesLabel release];
	
	[super dealloc];
}

- (void)setTask:(Task *)task target:(id)theTarget action:(SEL)theAction
{
	[super setTask:task target:theTarget action:theAction];
	
	categories = [[NSMutableArray alloc] init];
	Statement *req = [[Database connection] statementWithSQL:@"SELECT name FROM Category, TaskHasCategory WHERE id=idCategory AND idTask=?"];
	[req bindInteger:task.objectId atIndex:1];
	[req execWithTarget:self action:@selector(onCategory:)];
	categoriesLabel.text = [@", " stringByJoiningStrings:categories];
	[categories release];
	categories = nil;

	infosLabel.text = @"";
	
	switch ([task taskStatus])
	{
		case TASKSTATUS_COMPLETED:
			infosLabel.text = [NSString stringWithFormat:_("Completed %@"), task.completionDate];
			break;
		case TASKSTATUS_OVERDUE:
			infosLabel.text = [NSString stringWithFormat:_("Due %@"), task.dueDate];
			break;
		case TASKSTATUS_DUESOON:
			infosLabel.text = [NSString stringWithFormat:_("Due %@"), task.dueDate];
			break;
		case TASKSTATUS_STARTED:
			if (task.dueDate)
				infosLabel.text = [NSString stringWithFormat:_("Due %@"), task.dueDate];
		case TASKSTATUS_NOTSTARTED:
			if (task.startDate)
				infosLabel.text = [NSString stringWithFormat:_("Start %@"), task.startDate];
			break;
	}
}

- (void)onCategory:(NSDictionary *)dict
{
	[categories addObject:[dict objectForKey:@"name"]];
}

@end
