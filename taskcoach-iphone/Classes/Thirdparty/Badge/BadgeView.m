/*
 * Copyright (c) 2009 Josh Petrie
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *  
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#import "BadgeView.h"
#import "BadgeItem.h"

@implementation BadgeView

@synthesize margin;

const float kBadgeViewDefaultMargin = 3.0f;

const float kBadgeCapsulePadding = 2.0f;
const float kBadgeConcaveCapsuleClippingOffset = 1.0f;
const float kBadgeConcaveCapsuleClippingTrim = 3.0f;

#pragma mark Lifetime

- (void)initialize
{
	self.backgroundColor = [UIColor clearColor];

	primaryItem = [[BadgeItem alloc] init];
	annotations = [[NSMutableArray arrayWithCapacity:1] retain];
	
	margin = kBadgeViewDefaultMargin;
	
	self.text = nil;
	self.textColor = [UIColor whiteColor];
	self.capsuleColor = [UIColor grayColor];
	
	self.contentMode = UIViewContentModeRedraw;
}

- initWithCoder:(NSCoder *)encoder
{
	if ((self = [super initWithCoder:encoder])) {
		[self initialize];
	}
	
	return self;
}

- (id)initWithFrame:(CGRect)frame {
	if ((self = [super initWithFrame:frame])) {
		[self initialize];
	}
	
	return self;
}

- (void)dealloc {
	[primaryItem release];
	[annotations release];
	[super dealloc];
}

#pragma mark Content Management

- (NSString*)text {
	return primaryItem.text;
}

- (void)setText:(NSString *)value {
	primaryItem.text = value;
}

- (UIColor*)textColor {
	return primaryItem.textColor;
}

- (void)setTextColor:(UIColor *)value {
	primaryItem.textColor = value;
}

- (UIColor*)capsuleColor {
	return primaryItem.capsuleColor;
}

- (void) setCapsuleColor:(UIColor *)value {
	primaryItem.capsuleColor = value;
}

- (void)addAnnotation:(NSString*)itemText {
	[self addAnnotation:itemText capsuleColor:[UIColor grayColor]];
}

- (void)addAnnotation:(NSString*)itemText capsuleColor:(UIColor*)itemCapsuleColor {
	[self addAnnotation:itemText capsuleColor:itemCapsuleColor textColor:[UIColor whiteColor]];
}

- (void)addAnnotation:(NSString*)itemText capsuleColor:(UIColor*)itemCapsuleColor textColor:(UIColor*)itemTextColor {
	BadgeItem* annotation = [[BadgeItem alloc] init];
	annotation.text = itemText;
	annotation.textColor = itemTextColor;
	annotation.capsuleColor = itemCapsuleColor;
	[annotations addObject:annotation];
	[annotation release];
}

- (void)clearAnnotations {
	[annotations removeAllObjects];
}

- (BOOL)isEmpty
{
	if (self.text)
		return NO;

	return ([annotations count] == 0);
}

#pragma mark Drawing

- (CGRect)getBoundsForItem:(BadgeItem*)badgeItem withFont:(UIFont*)font facing:(NSInteger)facing {
	CGSize textBounds = [badgeItem.text sizeWithFont:font];
	
	// The purpose of this calculation is to ensure the label fits
	// attractively within the capsule shape, and to ensure that very
	// small labels don't cause the capsule to degenerate to a circle.
	CGFloat padding = MAX( textBounds.height / 2.0f, textBounds.height );
	if( facing < 0 ) {
		return CGRectMake( 0.0, 0.0, textBounds.width + textBounds.height / 4.0f, textBounds.height );
	} else {
		return CGRectMake( 0.0, 0.0, textBounds.width + padding, textBounds.height );
	}
}

- (void)drawCapsuleFor:(BadgeItem*)badgeItem inBounds:(CGRect)rectangle withFont:(UIFont*)font facing:(NSInteger)facing {
	CGContextRef context = UIGraphicsGetCurrentContext();;
	CGFloat radius = CGRectGetHeight( rectangle ) / 2.0f;
	CGFloat height = CGRectGetMinY( rectangle ) + CGRectGetHeight( rectangle) / 2.0f;
	CGFloat left = CGRectGetMinX(rectangle) + radius;
	CGFloat right = CGRectGetMaxX(rectangle) - radius;
	NSInteger leftCapDirection = 0;
	NSInteger rightCapDirection = 0;
	CGFloat arcStart = M_PI / 2.0f;
	CGFloat arcStop = M_PI * 3.0f / 2.0f;
	
	CGContextSaveGState( context );
	if( facing < 0 ) {
		// We're facing left, so the right cap becomes concave.
		right += 2.0f * radius;
		rightCapDirection = 1;
		
		CGContextClipToRect( context, CGRectMake(
			CGRectGetMinX( rectangle ) - kBadgeConcaveCapsuleClippingOffset,
			CGRectGetMinY( rectangle ),
			CGRectGetWidth( rectangle ) + radius - kBadgeConcaveCapsuleClippingTrim,
			CGRectGetHeight( rectangle )
		) );
	}
	
	CGContextSetFillColorWithColor( context, badgeItem.capsuleColor.CGColor );
	CGContextBeginPath( context );
	
	CGContextAddArc( context, left, height, radius, arcStart, arcStop, leftCapDirection );
	CGContextAddArc( context, right, height, radius, arcStop, arcStart, rightCapDirection );
	
	CGContextClosePath( context );
	CGContextFillPath(context);
	
	if( facing < 0 ) {
		rectangle = CGRectOffset( rectangle, CGRectGetHeight(rectangle) / 8.0f, 0.0f);
	}
	
	CGContextSetFillColorWithColor( context, badgeItem.textColor.CGColor );
	[badgeItem.text drawInRect:rectangle withFont:font lineBreakMode:UILineBreakModeClip alignment:UITextAlignmentCenter];
	CGContextRestoreGState(context);
}

- (void)drawRect:(CGRect)rect {
	if (!self.text)
		return;

	[super drawRect:rect];
	
	UIFont* font = [UIFont boldSystemFontOfSize:[UIFont systemFontSize]];
	
	CGRect rectangle = [self getBoundsForItem:primaryItem withFont:font facing:0];
	CGFloat x = CGRectGetMaxX( self.bounds ) - CGRectGetWidth( rectangle ) - margin;
	CGFloat y = ( CGRectGetMaxY( self.bounds ) - CGRectGetMaxY( rectangle ) ) / 2.0;
	rectangle = CGRectOffset( rectangle, x, y );
	[self drawCapsuleFor:primaryItem inBounds:rectangle withFont:font facing:0];
	CGFloat offset = -CGRectGetWidth( rectangle ) - kBadgeCapsulePadding;
	
	int facing = -1;
	for( BadgeItem* annotation in annotations ) {
		rectangle = [self getBoundsForItem:annotation withFont:font facing:facing];
		rectangle = CGRectOffset( rectangle, offset, 0.0);
		offset -= CGRectGetWidth( rectangle ) + kBadgeCapsulePadding;
		
		x = CGRectGetMaxX( self.bounds ) - CGRectGetWidth( rectangle ) - margin;
		y = ( CGRectGetMaxY( self.bounds ) - CGRectGetMaxY( rectangle ) ) / 2.0;
		rectangle = CGRectOffset( rectangle, x, y );
		
		[self drawCapsuleFor:annotation inBounds:rectangle withFont:font facing:facing];
		--facing;
	}
}

- (CGSize)sizeThatFits:(CGSize)size
{
	UIFont* font = [UIFont boldSystemFontOfSize:[UIFont systemFontSize]];
	
	CGRect rectangle = [self getBoundsForItem:primaryItem withFont:font facing:0];
	CGFloat x = CGRectGetMaxX( self.bounds ) - CGRectGetWidth( rectangle ) - margin;
	CGFloat y = ( CGRectGetMaxY( self.bounds ) - CGRectGetMaxY( rectangle ) ) / 2.0;
	rectangle = CGRectOffset( rectangle, x, y );
	CGFloat offset = -CGRectGetWidth( rectangle ) - kBadgeCapsulePadding;
	
	int facing = -1;
	for( BadgeItem* annotation in annotations )
	{
		rectangle = [self getBoundsForItem:annotation withFont:font facing:facing];
		rectangle = CGRectOffset( rectangle, offset, 0.0);
		offset -= CGRectGetWidth( rectangle ) + kBadgeCapsulePadding;

		// x = CGRectGetMaxX( self.bounds ) - CGRectGetWidth( rectangle ) - margin;
		// y = ( CGRectGetMaxY( self.bounds ) - CGRectGetMaxY( rectangle ) ) / 2.0;
		// rectangle = CGRectOffset( rectangle, x, y );
		
		--facing;
	}

	size.width = -offset + 2 * kBadgeViewDefaultMargin;
	
	return size;
}

@end
