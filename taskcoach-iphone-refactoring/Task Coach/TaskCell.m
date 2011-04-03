//
//  TaskCell.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "TaskCell.h"

#import "CDTask+Addons.h"
#import "String+Utils.h"
#import "CDCategory.h"

@implementation TaskCell

- (void)dealloc
{
    [super dealloc];
}

- (void)setTask:(CDTask *)task
{
    mainLabel.text = task.name;
    
    switch ([task.dateStatus intValue])
    {
        case TASKSTATUS_TRACKING:
            mainLabel.textColor = [[[UIColor alloc] initWithRed:0.7 green:0 blue:0 alpha:1.0] autorelease];
            break;
        case TASKSTATUS_OVERDUE:
            mainLabel.textColor = [UIColor redColor];
            break;
        case TASKSTATUS_DUESOON:
            mainLabel.textColor = [UIColor orangeColor];
            break;
        case TASKSTATUS_STARTED:
            mainLabel.textColor = [UIColor blueColor];
            break;
        case TASKSTATUS_NOTSTARTED:
            mainLabel.textColor = [UIColor grayColor];
            break;
        case TASKSTATUS_COMPLETED:
            mainLabel.textColor = [UIColor greenColor];
            break;
        default:
            mainLabel.textColor = [UIColor blackColor];
            break;
    }
    
    NSMutableArray *categoryNames = [[NSMutableArray alloc] init];
    for (CDCategory *category in task.categories)
        [categoryNames addObject:category.name];
    leftLabel.text = [@", " stringByJoiningStrings:categoryNames];
    [categoryNames release];
}

@end
