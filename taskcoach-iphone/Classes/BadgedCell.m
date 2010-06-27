//
//  BadgedCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/10/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "BadgedCell.h"

@implementation BadgedCell

@synthesize badge;
@synthesize textLabel;

- (CGSize)sizeThatFits:(CGSize)size
{
	return size;
}

- (void)layoutSubviews
{
	[self.badge sizeToFit];
	
	/*
	CGSize badgeSize = [self.badge sizeThatFits:self.badge.bounds.size];

	CGRect labelRect;
	labelRect.origin.x = 20 + 10 * self.indentationLevel;
	labelRect.origin.y = 11;
	labelRect.size.width = self.contentView.bounds.size.width - badgeSize.width - 60 - 10 * self.indentationLevel;
	labelRect.size.height = self.contentView.bounds.size.height - 22;
	self.textLabel.frame = labelRect;

	CGRect badgeRect;
	badgeRect.origin.x = labelRect.origin.x + labelRect.size.width + 10;
	badgeRect.origin.y = 11;
	badgeRect.size.width = badgeSize.width;
	badgeRect.size.height = self.contentView.bounds.size.height - 22;
	self.badge.frame = badgeRect;
	 */

	[super layoutSubviews];
}

- (void)willTransitionToState:(UITableViewCellStateMask)state
{
	self.badge.hidden = ((state & UITableViewCellStateEditingMask) != 0);

	[super willTransitionToState:state];

}

@end
